import React, { useState, useEffect } from "react";
import axios from "axios";
import { AdminAuthContext } from "./AdminAuthContext";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

export const AdminAuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(() => {
    const storedAdmin = localStorage.getItem("adminInfo");
    return storedAdmin ? JSON.parse(storedAdmin) : null;
  });

  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem("adminToken")
  );

  const [refreshToken, setRefreshToken] = useState(() =>
    localStorage.getItem("adminRefreshToken")
  );

  const loginAdmin = (adminData) => {
    setAdmin(adminData);
    localStorage.setItem("adminInfo", JSON.stringify(adminData));
    localStorage.setItem("adminToken", adminData.token);

    if (adminData.refreshToken) {
      setRefreshToken(adminData.refreshToken);
      localStorage.setItem("adminRefreshToken", adminData.refreshToken);
    }
    setAccessToken(adminData.token);
  };

  const logoutAdmin = () => {
    setAdmin(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("adminInfo");
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminRefreshToken");
  };

  // Axios 인터셉터를 이용하여 토큰 갱신 로직 구현
  useEffect(() => {
    // 인터셉터 추가: 모든 요청에 Authorization 헤더 자동 설정
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 응답 인터셉터 추가: 401 발생 시 토큰 갱신 시도
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        // 토큰 갱신 요청이 아니고 401 에러인 경우
        if (
          error.response &&
          error.response.status === 401 &&
          !originalRequest._retry
        ) {
          originalRequest._retry = true;
          // refreshToken이 없는 경우 바로 로그아웃
          if (!refreshToken) {
            console.error("리프레시 토큰이 없습니다.");
            logoutAdmin();
            return Promise.reject(error);
          }
          try {
            console.log("토큰 갱신 시도, 현재 refreshToken:", refreshToken);
            const refreshResponse = await axios.post(
              `${BASE_URL}/auth/refresh-token`,
              { refresh_token: refreshToken },
              { headers: { "Content-Type": "application/json" } }
            );
            if (refreshResponse.data.resultCode === "SUCCESS") {
              const newAccessToken = refreshResponse.data.data.access_token;
              const newRefreshToken = refreshResponse.data.data.refresh_token;
              setAccessToken(newAccessToken);
              setRefreshToken(newRefreshToken);

              console.log("Token refreshed successfully:", {
                newAccessToken,
                newRefreshToken,
              });

              localStorage.setItem("adminToken", newAccessToken);
              localStorage.setItem("adminRefreshToken", newRefreshToken);
              originalRequest.headers[
                "Authorization"
              ] = `Bearer ${newAccessToken}`;
              return axios(originalRequest);
            } else {
              console.error("토큰 갱신 응답 실패:", refreshResponse.data);
              logoutAdmin();
              return Promise.reject(error);
            }
          } catch (refreshError) {
            console.error("토큰 갱신 중 오류:", refreshError);
            logoutAdmin();
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [accessToken, refreshToken]);

  return (
    <AdminAuthContext.Provider
      value={{ admin, loginAdmin, logoutAdmin, accessToken }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};

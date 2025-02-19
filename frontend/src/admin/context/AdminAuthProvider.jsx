// src/admin/context/AdminAuthProvider.jsx
import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { AdminAuthContext } from "./AdminAuthContext";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const BASE_URL = import.meta.env.VITE_API_URL;

export const AdminAuthProvider = ({ children }) => {
  const navigate = useNavigate();
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

  // ref를 사용하여 로그아웃 처리 중임을 추적
  const isLoggingOutRef = useRef(false);
  // 현재 진행 중인 토큰 갱신 요청을 저장할 ref
  const refreshPromiseRef = useRef(null);

  const loginAdmin = (adminData) => {
    setAdmin(adminData);
    localStorage.setItem("adminInfo", JSON.stringify(adminData));
    localStorage.setItem("adminToken", adminData.token);
    if (adminData.refreshToken) {
      setRefreshToken(adminData.refreshToken);
      localStorage.setItem("adminRefreshToken", adminData.refreshToken);
    }
    setAccessToken(adminData.token);
    isLoggingOutRef.current = false;
  };

  const logoutAdmin = () => {
    if (isLoggingOutRef.current) return;
    isLoggingOutRef.current = true;
    setAdmin(null);
    setAccessToken(null);
    setRefreshToken(null);
    localStorage.removeItem("adminInfo");
    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminRefreshToken");
  };

  // 토큰 갱신 함수
  const refreshTokens = async () => {
    if (!refreshToken) {
      throw new Error("리프레시 토큰이 없습니다.");
    }
    if (!refreshPromiseRef.current) {
      refreshPromiseRef.current = axios.post(
        `${BASE_URL}/auth/refresh-token`,
        { refresh_token: refreshToken },
        { headers: { "Content-Type": "application/json" } }
      );
    }
    const refreshResponse = await refreshPromiseRef.current;
    refreshPromiseRef.current = null;
    if (refreshResponse.data.resultCode === "SUCCESS") {
      const newAccessToken = refreshResponse.data.data.access_token;
      const newRefreshToken = refreshResponse.data.data.refresh_token;
      setAccessToken(newAccessToken);
      setRefreshToken(newRefreshToken);
      localStorage.setItem("adminToken", newAccessToken);
      localStorage.setItem("adminRefreshToken", newRefreshToken);
      toast.info("세션이 연장되었습니다.");
      return newAccessToken;
    } else {
      throw new Error("토큰 갱신 응답 실패");
    }
  };

  const getTimeLeft = (token) => {
    try {
      const decoded = jwtDecode(token);
      if (!decoded.exp) return 0;
      const expiryTime = decoded.exp * 1000;
      const currentTime = Date.now();
      return expiryTime - currentTime;
    } catch (error) {
      console.error("토큰 디코딩 오류:", error);
      return 0;
    }
  };

  /**
   *   useEffect(() => {
    if (!accessToken || !refreshToken) return;

    const threshold = 1 * 60 * 1000; // 지금은 1분, 해당 시간이 되면 자동으로 토큰을 갱신 시도한다.
    const intervalId = setInterval(async () => {
      const timeLeft = getTimeLeft(accessToken);
      // console.log("토큰 남은 시간:", timeLeft);
      if (timeLeft < threshold) {
        if (!refreshPromiseRef.current) {
          refreshPromiseRef.current = axios
            .post(
              `${BASE_URL}/auth/refresh-token`,
              { refresh_token: refreshToken },
              { headers: { "Content-Type": "application/json" } }
            )
            .then((refreshResponse) => {
              refreshPromiseRef.current = null;
              if (refreshResponse.data.resultCode === "SUCCESS") {
                const newAccessToken = refreshResponse.data.data.access_token;
                const newRefreshToken = refreshResponse.data.data.refresh_token;
                setAccessToken(newAccessToken);
                setRefreshToken(newRefreshToken);
                localStorage.setItem("adminToken", newAccessToken);
                localStorage.setItem("adminRefreshToken", newRefreshToken);
                toast.info("세션이 연장되었습니다.");
              } else {
                throw new Error("토큰 갱신 응답 실패");
              }
            })
            .catch((error) => {
              refreshPromiseRef.current = null;
              console.error("자동 토큰 갱신 실패:", error);
              if (!isLoggingOutRef.current) {
                toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
                logoutAdmin();
                navigate("/admin/login");
              }
            });
        }
      }
    }, 30 * 1000); // 현재는 30초마다 확인을 한다.

    return () => clearInterval(intervalId);
  }, [accessToken, refreshToken, navigate]);
   */

  useEffect(() => {
    // 요청 인터셉터: 모든 요청에 Authorization 헤더 자동 설정
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers["Authorization"] = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (
          error.response &&
          error.response.status === 401 &&
          !originalRequest._retry
        ) {
          toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
          logoutAdmin();
          navigate("/admin/login");
        }
        return Promise.reject(error);
      }
    );

    /**
     * 
     * // 응답 인터셉터: 401 에러 발생 시 토큰 갱신 시도
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        // _retry가 없고, 401 오류인 경우에만 토큰 갱신 시도
        if (
          error.response &&
          error.response.status === 401 &&
          !originalRequest._retry
        ) {
          originalRequest._retry = true;
          if (!refreshPromiseRef.current) {
            refreshPromiseRef.current = axios.post(
              `${BASE_URL}/auth/refresh-token`,
              { refresh_token: refreshToken },
              { headers: { "Content-Type": "application/json" } }
            );
          }
          try {
            const refreshResponse = await refreshPromiseRef.current;
            refreshPromiseRef.current = null; // 갱신 완료 후 초기화

            if (refreshResponse.data.resultCode === "SUCCESS") {
              const newAccessToken = refreshResponse.data.data.access_token;
              const newRefreshToken = refreshResponse.data.data.refresh_token;
              setAccessToken(newAccessToken);
              setRefreshToken(newRefreshToken);
              localStorage.setItem("adminToken", newAccessToken);
              localStorage.setItem("adminRefreshToken", newRefreshToken);
              originalRequest.headers[
                "Authorization"
              ] = `Bearer ${newAccessToken}`;
              return axios(originalRequest);
            } else {
              console.error("토큰 갱신 응답 실패:", refreshResponse.data);
              if (!isLoggingOutRef.current) {
                toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
                logoutAdmin();
                navigate("/admin/login");
              }
              return Promise.reject(error);
            }
          } catch (refreshError) {
            refreshPromiseRef.current = null;
            console.error("토큰 갱신 중 오류:", refreshError);
            if (!isLoggingOutRef.current) {
              toast.error("세션이 만료되었습니다. 다시 로그인 해주세요.");
              logoutAdmin();
              navigate("/admin/login");
            }
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );
     */

    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, [accessToken, refreshToken, navigate]);

  return (
    <AdminAuthContext.Provider
      value={{ admin, loginAdmin, logoutAdmin, accessToken, refreshTokens }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
};

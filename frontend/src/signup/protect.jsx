import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ children }) => {
    const token = sessionStorage.getItem("token"); // 토큰 가져오기

    if (!token) {
        alert("로그인이 필요합니다!");
        return <Navigate to="/login" />; // 로그인 페이지로 리디렉션
    }

    return children;
};

export default ProtectedRoute;

// src/admin/components/ModuleInstallVideoModal.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import "./ModuleVideoModal.css";
import LoadingSpinner from "./LoadingSpinner";

const BASE_URL = import.meta.env.VITE_API_URL;

function ModuleInstallVideoModal({ rentId, onClose }) {
  const token = localStorage.getItem("adminToken");
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchVideos = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await axios.get(
          `${BASE_URL}/admin/rent-history/${rentId}/module-install-videos`,
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: token ? `Bearer ${token}` : undefined,
            },
          }
        );
        if (response.data.resultCode === "SUCCESS") {
          setVideos(response.data.data.videos);
        } else {
          setError(response.data.message || "모듈 설치 영상 조회 실패");
        }
      } catch (err) {
        console.error(err);
        setError("모듈 설치 영상 조회 중 오류 발생");
      } finally {
        setLoading(false);
      }
    };

    fetchVideos();
  }, [rentId, token]);

  return (
    <div className="video-modal-overlay" onClick={onClose}>
      <div className="video-modal" onClick={(e) => e.stopPropagation()}>
        <h2>모듈 설치 영상</h2>
        <button className="close-button" onClick={onClose}>
          &times;
        </button>
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <p className="error">{error}</p>
        ) : videos.length > 0 ? (
          videos.map((video) => (
            <div key={video.video_id} className="video-item">
              <p>
                <strong>비디오 ID:</strong> {video.video_id}
              </p>
              <p>
                <strong>대여 ID:</strong> {video.rent_id}
              </p>
              <p>
                <strong>타입:</strong> {video.video_type}
              </p>
              <p>
                <strong>녹화 시각:</strong>{" "}
                {new Date(video.recorded_at).toLocaleString()}
              </p>
              <video width="100%" controls>
                <source src={video.video_url} type="video/mp4" />
                브라우저가 동영상을 지원하지 않습니다.
              </video>
            </div>
          ))
        ) : (
          <p>영상이 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default ModuleInstallVideoModal;

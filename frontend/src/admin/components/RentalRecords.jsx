// src/components/RentalRecords.jsx

import React, { useState, useEffect } from "react";
import Modal from "./Modal";
import "./RentalRecords.css";
import { MdVideoLibrary, MdSearch, MdVideocam } from "react-icons/md";

function RentalRecords() {
  /**
   * 초기 더미 데이터 설정
   * 대여 로그 목록을 더미 데이터로 관리.
   */
  const initialDummyRentLogs = [
    {
      rentId: 101,
      user: {
        userId: "user123",
        userName: "김철수",
        userEmail: "user123@example.com",
        userPhone: "010-1234-5678",
      },
      vehicle: {
        vehicleId: 50,
        vin: "VIN123456789",
        vehicleNumber: "PBV-1234",
      },
      modules: [
        {
          moduleId: 301,
          moduleName: "배터리 팩",
          quantity: 1,
        },
        {
          moduleId: 302,
          moduleName: "냉장고",
          quantity: 2,
        },
      ],
      rentalPeriod: {
        startDate: "2025-01-01",
        endDate: "2025-01-05",
      },
      rentCost: 500000,
      distanceTravelled: 120,
      status: "completed",
      createdAt: "2025-01-01T08:00:00Z",
      updatedAt: "2025-01-05T18:00:00Z",
      autonomousDrivingLog: {
        rentId: 101,
        user: {
          userId: "user123",
          userName: "김철수",
          userEmail: "user123@example.com",
          userPhone: "010-1234-5678",
        },
        vehicle: {
          vehicleId: 50,
          vin: "VIN123456789",
          vehicleNumber: "PBV-1234",
        },
        rentStartDate: "2025-01-01",
        rentEndDate: "2025-01-05",
        autonomousVideos: [
          {
            videoId: 301,
            videoUrl: "https://example.com/video1.mp4",
            recordedAt: "2025-01-02T14:30:00Z",
          },
          {
            videoId: 302,
            videoUrl: "https://example.com/video2.mp4",
            recordedAt: "2025-01-03T10:00:00Z",
          },
        ],
        errorLogs: [
          {
            errorId: 201,
            timestamp: "2025-01-03T14:30:00Z",
            errorCode: "SENSOR_FAILURE",
            message: "Sensor malfunction detected",
          },
          {
            errorId: 202,
            timestamp: "2025-01-04T09:15:00Z",
            errorCode: "GPS_LOST",
            message: "GPS signal lost",
          },
        ],
        destination: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
        status: "completed",
        totalDistance: 120,
        totalCost: 500000,
      },
      moduleVideo: {
        videoId: "VID123456",
        rentId: "RENT101",
        videoUrl:
          "https://s3.amazonaws.com/bucket-name/videos/RENT101-module.mp4",
        videoMetadata: {
          size: "25MB",
          format: "mp4",
          duration: "00:03:45",
          recordedAt: "2025-01-02T14:30:00Z",
        },
      },
    },
    {
      rentId: 102,
      user: {
        userId: "user456",
        userName: "이영희",
        userEmail: "user456@example.com",
        userPhone: "010-9876-5432",
      },
      vehicle: {
        vehicleId: 51,
        vin: "VIN987654321",
        vehicleNumber: "PBV-5678",
      },
      modules: [
        {
          moduleId: 303,
          moduleName: "태양광 패널",
          quantity: 1,
        },
      ],
      rentalPeriod: {
        startDate: "2025-01-10",
        endDate: "2025-01-15",
      },
      rentCost: 750000,
      distanceTravelled: 200,
      status: "in_progress",
      createdAt: "2025-01-10T08:00:00Z",
      updatedAt: "2025-01-12T12:00:00Z",
      autonomousDrivingLog: {
        rentId: 102,
        user: {
          userId: "user456",
          userName: "이영희",
          userEmail: "user456@example.com",
          userPhone: "010-9876-5432",
        },
        vehicle: {
          vehicleId: 51,
          vin: "VIN987654321",
          vehicleNumber: "PBV-5678",
        },
        rentStartDate: "2025-01-10",
        rentEndDate: "2025-01-15",
        autonomousVideos: [
          {
            videoId: 303,
            videoUrl: "https://example.com/video3.mp4",
            recordedAt: "2025-01-11T10:30:00Z",
          },
        ],
        errorLogs: [
          {
            errorId: 203,
            timestamp: "2025-01-11T12:00:00Z",
            errorCode: "ENGINE_OVERHEAT",
            message: "Engine temperature exceeded safe limits",
          },
        ],
        destination: {
          latitude: 35.1796,
          longitude: 129.0756,
        },
        status: "in_progress",
        totalDistance: 150,
        totalCost: 750000,
      },
      moduleVideo: {
        videoId: "VID123457",
        rentId: "RENT102",
        videoUrl:
          "https://s3.amazonaws.com/bucket-name/videos/RENT102-module.mp4",
        videoMetadata: {
          size: "30MB",
          format: "mp4",
          duration: "00:04:20",
          recordedAt: "2025-01-11T10:30:00Z",
        },
      },
    },
  ];

  // 대여 로그 목록 상태: 초기 더미 데이터로 설정
  const [rentLogs, setRentLogs] = useState([]);

  // 모달 관리 상태
  const [modalType, setModalType] = useState(null); // 'detail', 'autonomousVideo', 'moduleVideo'
  const [selectedRentLog, setSelectedRentLog] = useState(null); // 선택된 대여 로그

  // 필터 상태
  const [filters, setFilters] = useState({
    userId: "",
    carId: "",
    startDate: "",
    endDate: "",
    page: 1,
    pageSize: 10,
  });

  // 페이지네이션 상태
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });

  // 로딩 및 오류 상태
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 관리자 인증 토큰 (필요 시 설정)
  const token = localStorage.getItem("adminToken"); // 토큰 저장 방식에 따라 수정

  // API 베이스 URL 설정
  const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

  /**
   * 대여 로그 목록 조회 함수
   * 현재는 더미 데이터를 사용하지만, 추후 API 연동 시 수정 필요.
   */
  const fetchRentLogs = () => {
    setLoading(true);
    setError("");
    try {
      /**
       * !!! 이 부분은 최신 버전으로 갱신해야 함
       */

      // API 연동 시 주석 해제하고 사용
      /*
      const response = await axios.get(`${BASE_URL}/admin/rent-history`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          userId: filters.userId || undefined,
          carId: filters.carId || undefined,
          startDate: filters.startDate || undefined,
          endDate: filters.endDate || undefined,
          page: filters.page,
          pageSize: filters.pageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setRentLogs(response.data.data.rentLogs);
        setPagination(response.data.data.pagination);
      } else {
        setError(response.data.message || "대여 로그를 불러오는 데 실패했습니다.");
        setRentLogs(initialDummyRentLogs);
      }
      */

      // 현재는 더미 데이터 사용
      let filteredRentLogs = [...initialDummyRentLogs];

      if (filters.userId) {
        filteredRentLogs = filteredRentLogs.filter((log) =>
          log.user.userId.toLowerCase().includes(filters.userId.toLowerCase())
        );
      }

      if (filters.carId) {
        filteredRentLogs = filteredRentLogs.filter(
          (log) =>
            log.vehicle.vehicleId.toString() === filters.carId ||
            log.vehicle.vehicleNumber
              .toLowerCase()
              .includes(filters.carId.toLowerCase())
        );
      }

      if (filters.startDate) {
        filteredRentLogs = filteredRentLogs.filter(
          (log) =>
            new Date(log.rentalPeriod.startDate) >= new Date(filters.startDate)
        );
      }

      if (filters.endDate) {
        filteredRentLogs = filteredRentLogs.filter(
          (log) =>
            new Date(log.rentalPeriod.endDate) <= new Date(filters.endDate)
        );
      }

      // 페이지네이션 적용
      const startIndex = (filters.page - 1) * filters.pageSize;
      const endIndex = startIndex + filters.pageSize;
      const paginatedRentLogs = filteredRentLogs.slice(startIndex, endIndex);

      setRentLogs(paginatedRentLogs);
      setPagination({
        currentPage: filters.page,
        totalPages: Math.ceil(filteredRentLogs.length / filters.pageSize),
        totalItems: filteredRentLogs.length,
        pageSize: filters.pageSize,
      });
    } catch (err) {
      console.error(err);
      setError("대여 로그를 불러오는 중 오류가 발생했습니다.");
      setRentLogs(initialDummyRentLogs);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 및 필터 변경 시 대여 로그 목록 조회
  useEffect(() => {
    fetchRentLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
      // 필터 변경 시 페이지를 1로 리셋
      ...(name === "userId" ||
      name === "carId" ||
      name === "startDate" ||
      name === "endDate"
        ? { page: 1 }
        : {}),
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prevFilters) => ({
      ...prevFilters,
      page: newPage,
    }));
  };

  // 모달 열기 함수
  const openModal = (type, rentLog = null) => {
    setModalType(type);
    setSelectedRentLog(rentLog);
  };

  // 모달 닫기 함수
  const closeModal = () => {
    setModalType(null);
    setSelectedRentLog(null);
    setError("");
  };

  return (
    <div className="rental-container">
      <div className="rental-header">
        <h1>대여 로그 조회</h1>
      </div>

      {/* 필터링 섹션 */}
      <div className="filters">
        <label>
          사용자 ID
          <input
            type="text"
            name="userId"
            value={filters.userId}
            onChange={handleFilterChange}
            placeholder="사용자 ID 입력"
          />
        </label>
        <label>
          차량 ID/번호
          <input
            type="text"
            name="carId"
            value={filters.carId}
            onChange={handleFilterChange}
            placeholder="차량 ID 또는 번호 입력"
          />
        </label>
        <label>
          시작 날짜
          <input
            type="date"
            name="startDate"
            value={filters.startDate}
            onChange={handleFilterChange}
          />
        </label>
        <label>
          종료 날짜
          <input
            type="date"
            name="endDate"
            value={filters.endDate}
            onChange={handleFilterChange}
          />
        </label>
        <button onClick={fetchRentLogs}>검색</button>
      </div>

      {/* 대여 로그 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <table className="rental-table">
            <thead>
              <tr>
                <th>대여 ID</th>
                <th>사용자 ID</th>
                <th>사용자 이름</th>
                <th>차량 번호</th>
                <th>대여 상태</th>
                <th>대여 기간</th>
                <th>대여 비용 (원)</th>
                <th>주행 거리 (km)</th>
                <th>등록 일자</th>
                <th>상세 보기</th>
                <th>자율 주행 영상</th>
                <th>모듈 장착 영상</th>
              </tr>
            </thead>
            <tbody>
              {rentLogs.length > 0 ? (
                rentLogs.map((log) => (
                  <tr key={log.rentId}>
                    <td>{log.rentId}</td>
                    <td>{log.user.userId}</td>
                    <td>{log.user.userName}</td>
                    <td>{log.vehicle.vehicleNumber}</td>
                    <td>
                      {log.status === "reserved"
                        ? "예약됨"
                        : log.status === "in_progress"
                        ? "진행 중"
                        : log.status === "completed"
                        ? "완료됨"
                        : "취소됨"}
                    </td>
                    <td>
                      {log.rentalPeriod.startDate} ~ {log.rentalPeriod.endDate}
                    </td>
                    <td>{log.rentCost.toLocaleString()}원</td>
                    <td>{log.distanceTravelled} km</td>
                    <td>{new Date(log.createdAt).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => openModal("detail", log)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                    <td>
                      <button
                        className="video-button"
                        onClick={() => openModal("autonomousVideo", log)}
                      >
                        <MdVideoLibrary />
                      </button>
                    </td>
                    <td>
                      <button
                        className="video-button"
                        onClick={() => openModal("moduleVideo", log)}
                      >
                        <MdVideocam />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="12">조회된 대여 로그가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>

          {/* 페이지네이션 */}
          <div className="pagination">
            <button
              onClick={() => handlePageChange(pagination.currentPage - 1)}
              disabled={pagination.currentPage === 1}
            >
              이전
            </button>
            <span>
              {pagination.currentPage} / {pagination.totalPages}
            </span>
            <button
              onClick={() => handlePageChange(pagination.currentPage + 1)}
              disabled={pagination.currentPage === pagination.totalPages}
            >
              다음
            </button>
          </div>
        </>
      )}

      {/* 모달 */}
      <Modal isOpen={modalType !== null} onClose={closeModal}>
        {/* 상세 정보 모달 */}
        {modalType === "detail" && selectedRentLog && (
          <div className="detail-content">
            <h2>대여 로그 상세 정보</h2>
            <p>대여 ID: {selectedRentLog.rentId}</p>
            <p>사용자 ID: {selectedRentLog.user.userId}</p>
            <p>사용자 이름: {selectedRentLog.user.userName}</p>
            <p>사용자 이메일: {selectedRentLog.user.userEmail}</p>
            <p>사용자 전화번호: {selectedRentLog.user.userPhone}</p>
            <p>차량 번호: {selectedRentLog.vehicle.vehicleNumber}</p>
            <p>차량 VIN: {selectedRentLog.vehicle.vin}</p>
            <p>
              대여 상태:{" "}
              {selectedRentLog.status === "reserved"
                ? "예약됨"
                : selectedRentLog.status === "in_progress"
                ? "진행 중"
                : selectedRentLog.status === "completed"
                ? "완료됨"
                : "취소됨"}
            </p>
            <p>
              대여 기간: {selectedRentLog.rentalPeriod.startDate} ~{" "}
              {selectedRentLog.rentalPeriod.endDate}
            </p>
            <p>대여 비용: {selectedRentLog.rentCost.toLocaleString()}원</p>
            <p>주행 거리: {selectedRentLog.distanceTravelled} km</p>
            <p>
              등록 일자: {new Date(selectedRentLog.createdAt).toLocaleString()}
            </p>
            <p>
              최종 업데이트:{" "}
              {new Date(selectedRentLog.updatedAt).toLocaleString()}
            </p>

            {/* 모듈 정보 */}
            <h3>장착된 모듈</h3>
            <ul>
              {selectedRentLog.modules.map((module) => (
                <li key={module.moduleId}>
                  {module.moduleName} x {module.quantity}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 자율 주행 영상 모달 */}
        {modalType === "autonomousVideo" && selectedRentLog && (
          <div className="autonomous-video-content">
            <h2>자율 주행 로그</h2>
            <p>
              목적지: 위도{" "}
              {selectedRentLog.autonomousDrivingLog.destination.latitude}, 경도{" "}
              {selectedRentLog.autonomousDrivingLog.destination.longitude}
            </p>
            <p>
              상태:{" "}
              {selectedRentLog.autonomousDrivingLog.status === "in_progress"
                ? "진행 중"
                : "완료됨"}
            </p>
            <p>
              총 거리: {selectedRentLog.autonomousDrivingLog.totalDistance} km
            </p>
            <p>
              총 비용:{" "}
              {selectedRentLog.autonomousDrivingLog.totalCost.toLocaleString()}
              원
            </p>

            <h3>자율 주행 영상</h3>
            {selectedRentLog.autonomousDrivingLog.autonomousVideos.length >
            0 ? (
              selectedRentLog.autonomousDrivingLog.autonomousVideos.map(
                (video) => (
                  <div key={video.videoId} className="video-section">
                    <p>영상 ID: {video.videoId}</p>
                    <video width="100%" height="auto" controls>
                      <source src={video.videoUrl} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                    <p>
                      녹화 시간: {new Date(video.recordedAt).toLocaleString()}
                    </p>
                  </div>
                )
              )
            ) : (
              <p>자율 주행 영상이 없습니다.</p>
            )}

            <h3>오류 로그</h3>
            {selectedRentLog.autonomousDrivingLog.errorLogs.length > 0 ? (
              <ul>
                {selectedRentLog.autonomousDrivingLog.errorLogs.map((error) => (
                  <li key={error.errorId}>
                    [{new Date(error.timestamp).toLocaleString()}]{" "}
                    {error.errorCode}: {error.message}
                  </li>
                ))}
              </ul>
            ) : (
              <p>오류 로그가 없습니다.</p>
            )}
          </div>
        )}

        {/* 모듈 장착 영상 모달 */}
        {modalType === "moduleVideo" && selectedRentLog && (
          <div className="module-video-content">
            <h2>모듈 장착 영상</h2>
            {selectedRentLog.moduleVideo ? (
              <>
                <p>영상 ID: {selectedRentLog.moduleVideo.videoId}</p>
                <video width="100%" height="auto" controls>
                  <source
                    src={selectedRentLog.moduleVideo.videoUrl}
                    type="video/mp4"
                  />
                  Your browser does not support the video tag.
                </video>
                <p>
                  영상 크기: {selectedRentLog.moduleVideo.videoMetadata.size}
                </p>
                <p>포맷: {selectedRentLog.moduleVideo.videoMetadata.format}</p>
                <p>
                  길이: {selectedRentLog.moduleVideo.videoMetadata.duration}
                </p>
                <p>
                  녹화 시간:{" "}
                  {new Date(
                    selectedRentLog.moduleVideo.videoMetadata.recordedAt
                  ).toLocaleString()}
                </p>
              </>
            ) : (
              <p>모듈 장착 영상이 없습니다.</p>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default RentalRecords;

// src/admin/components/ModuleSetManagement.jsx
import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import Modal from "./Modal";
import { MdSearch, MdEdit, MdDelete } from "react-icons/md";
import "./ModuleManagement.css";

const BASE_URL = "https://backend-wandering-river-6835.fly.dev";

const ModuleSetManagement = () => {
  const token = localStorage.getItem("adminToken");

  const [moduleSets, setModuleSets] = useState([]);
  const [selectedModuleSet, setSelectedModuleSet] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalContentType, setModalContentType] = useState("detail");
  const [formData, setFormData] = useState({
    module_set_name: "",
    description: "",
    cost: "",
    module_set_images: "",
  });
  const [filters, setFilters] = useState({
    moduleSetSearch: "",
    moduleSetPage: 1,
    moduleSetPageSize: 10,
  });
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 모듈 세트 목록 조회 함수
  const fetchModuleSets = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/module-sets`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        params: {
          search: filters.moduleSetSearch || undefined,
          page: filters.moduleSetPage,
          pageSize: filters.moduleSetPageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setModuleSets(response.data.data.module_sets);
        setPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "모듈 세트 목록을 불러오는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트 목록을 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }, [filters, token]);

  useEffect(() => {
    fetchModuleSets();
  }, [fetchModuleSets]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
      moduleSetPage: 1,
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (newPage) => {
    setFilters((prev) => ({
      ...prev,
      moduleSetPage: newPage,
    }));
  };

  // 모듈 세트 수정
  const handleEditClick = () => {
    setFormData({
      module_set_name: selectedModuleSet.module_set_name,
      description: selectedModuleSet.description,
      cost: selectedModuleSet.cost,
      module_set_images: selectedModuleSet.module_set_images,
    });
    setModalContentType("edit");
  };

  // 모듈 세트 삭제
  const handleDeleteClick = () => {
    setModalContentType("delete");
  };

  // 신규 등록 모달 열기
  const handleAddClick = () => {
    setFormData({
      module_set_name: "",
      description: "",
      cost: "",
      module_set_images: "",
    });
    setModalContentType("add");
    setIsModalOpen(true);
  };

  // 폼 입력 변경 핸들러
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // 신규 모듈 세트 저장 (서버 연동)
  const handleSaveAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = { ...formData };

      const response = await axios.post(
        `${BASE_URL}/admin/module-sets`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets(); // 새로 추가된 모듈 세트를 목록에 반영
        closeModal(); // 모달 닫기
      } else {
        setError(
          response.data.message || "모듈 세트를 등록하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트를 등록하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 모듈 세트 수정 저장
  const handleSaveEdit = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = { ...formData };

      const response = await axios.patch(
        `${BASE_URL}/admin/module-sets/${selectedModuleSet.module_set_id}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트 정보를 수정하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트 정보를 수정하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 모듈 세트 삭제 확인
  const handleConfirmDelete = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-sets/${selectedModuleSet.module_set_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 삭제하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      setError("모듈 세트를 삭제하는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  // 모달 닫기
  const closeModal = () => {
    setSelectedModuleSet(null);
    setIsModalOpen(false);
  };

  return (
    <div className="module-set-management">
      <div className="filters">
        <h2>모듈 세트 목록</h2>
        <label>
          검색
          <input
            type="text"
            name="moduleSetSearch"
            value={filters.moduleSetSearch}
            onChange={handleFilterChange}
            placeholder="모듈 세트 이름 검색"
          />
        </label>
        <button onClick={fetchModuleSets}>검색</button>
      </div>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <div className="table-wrapper">
          <table className="module-set-table">
            <thead>
              <tr>
                <th>모듈 세트 ID</th>
                <th>모듈 세트 이름</th>
                <th>설명</th>
                <th>이미지</th>
                <th>기능</th>
                <th>가격</th>
                <th>수정</th>
                <th>삭제</th>
              </tr>
            </thead>
            <tbody>
              {moduleSets.length > 0 ? (
                moduleSets.map((set) => (
                  <tr key={set.module_set_id}>
                    <td>{set.module_set_id}</td>
                    <td>{set.module_set_name}</td>
                    <td>{set.description}</td>
                    <td>
                      {set.module_set_images ? (
                        <img
                          src={set.module_set_images}
                          alt={set.module_set_name}
                          className="module-set-image"
                        />
                      ) : (
                        "이미지 없음"
                      )}
                    </td>
                    <td>{set.module_set_features}</td>
                    <td>{set.cost}</td>
                    <td>
                      <button
                        className="edit-button"
                        onClick={() => {
                          setSelectedModuleSet(set);
                          handleEditClick();
                        }}
                      >
                        <MdEdit />
                      </button>
                    </td>
                    <td>
                      <button
                        className="delete-button"
                        onClick={() => {
                          setSelectedModuleSet(set);
                          handleDeleteClick();
                        }}
                      >
                        <MdDelete />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8">조회된 모듈 세트가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* 페이지네이션 */}
      <div className="pagination">
        <button
          onClick={() => handlePageChange(filters.moduleSetPage - 1)}
          disabled={filters.moduleSetPage === 1}
        >
          이전
        </button>
        <span>
          {filters.moduleSetPage} / {pagination.totalPages}
        </span>
        <button
          onClick={() => handlePageChange(filters.moduleSetPage + 1)}
          disabled={filters.moduleSetPage === pagination.totalPages}
        >
          다음
        </button>
      </div>

      {/* 신규 등록 모달 */}
      <Modal isOpen={isModalOpen} onClose={closeModal} title="모듈 세트 관리">
        {modalContentType === "detail" && selectedModuleSet && (
          <div className="detail-content">
            <p>모듈 세트 이름: {selectedModuleSet.module_set_name}</p>
            <p>설명: {selectedModuleSet.description}</p>
            <p>가격: {selectedModuleSet.cost}</p>
            <div className="modal-actions">
              <button onClick={handleEditClick} className="edit-button">
                수정
              </button>
              <button onClick={handleDeleteClick} className="delete-button">
                삭제
              </button>
            </div>
          </div>
        )}

        {modalContentType === "edit" && selectedModuleSet && (
          <div className="edit-content">
            <form>
              <label>
                모듈 세트 이름:
                <input
                  type="text"
                  name="module_set_name"
                  value={formData.module_set_name}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                설명:
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                가격:
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                />
              </label>
            </form>
            <div className="modal-actions">
              <button onClick={handleSaveEdit} className="save-button">
                저장
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {modalContentType === "delete" && selectedModuleSet && (
          <div className="delete-content">
            <h2>모듈 세트 삭제 확인</h2>
            <p>정말로 이 모듈 세트를 삭제하시겠습니까?</p>
            <div className="modal-actions">
              <button
                onClick={handleConfirmDelete}
                className="confirm-delete-button"
              >
                삭제
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {modalContentType === "add" && (
          <div className="add-content">
            <form>
              <label>
                모듈 세트 이름:
                <input
                  type="text"
                  name="module_set_name"
                  value={formData.module_set_name}
                  onChange={handleFormChange}
                  required
                />
              </label>
              <label>
                설명:
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleFormChange}
                />
              </label>
              <label>
                가격:
                <input
                  type="number"
                  name="cost"
                  value={formData.cost}
                  onChange={handleFormChange}
                  required
                />
              </label>
            </form>
            <div className="modal-actions">
              <button onClick={handleSaveAdd} className="save-button">
                등록
              </button>
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ModuleSetManagement;

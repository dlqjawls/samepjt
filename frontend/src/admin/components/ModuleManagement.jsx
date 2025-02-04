// src/components/ModuleManagement.jsx

import React, { useState, useEffect } from "react";
import axios from "axios";
import Modal from "./Modal";
import "./ModuleManagement.css";
import { MdSearch } from "react-icons/md";

function ModuleManagement() {
  /**
   * 초기 더미 데이터 설정
   * 모듈 세트와 모듈 각각에 대한 더미 데이터를 정의.
   */
  const initialDummyModuleSets = [
    {
      moduleSetId: 101,
      moduleSetName: "캠핑카 모듈 세트",
      totalCost: 250000,
      imgUrls: ["https://example.com/images/module-set-101.jpg"],
      description: "캠핑을 위한 완벽한 모듈 세트",
      options: [
        { optionId: 201, optionName: "배터리 팩", quantity: 1 },
        { optionId: 202, optionName: "태양광 패널", quantity: 2 },
      ],
    },
    {
      moduleSetId: 102,
      moduleSetName: "기본 모듈 세트",
      totalCost: 150000,
      imgUrls: [],
      description: "옵션이 없는 기본 모듈 세트",
      options: [],
    },
  ];

  const initialDummyModules = [
    {
      moduleId: 1,
      moduleNfcTagId: "NFC123456",
      moduleType: "센서",
      moduleSize: "Small",
      moduleCost: 30000,
      status: "active",
      lastMaintenanceAt: "2024-11-15",
      nextMaintenanceAt: "2025-02-15",
      currentLocation: "창고",
      createdAt: "2024-10-01T08:00",
      updatedAt: "2024-11-01T08:00",
    },
    {
      moduleId: 2,
      moduleNfcTagId: "NFC654321",
      moduleType: "카메라",
      moduleSize: "Large",
      moduleCost: 70000,
      status: "maintenance",
      lastMaintenanceAt: "2024-10-10",
      nextMaintenanceAt: "2025-01-10",
      currentLocation: "정비소",
      createdAt: "2024-09-20T09:00",
      updatedAt: "2024-11-05T09:00",
    },
  ];

  // 모듈 세트 및 모듈 목록 상태: 초기 더미 데이터로 설정
  const [moduleSets, setModuleSets] = useState(initialDummyModuleSets);
  const [modules, setModules] = useState(initialDummyModules);

  // 모달 관리 상태
  const [modalType, setModalType] = useState(null); // 'addModuleSet', 'addModule', 'detailModuleSet', 'detailModule', 'editModuleSet', 'editModule', 'deleteModuleSet', 'deleteModule'
  const [selectedItem, setSelectedItem] = useState(null); // 선택된 모듈 세트 또는 모듈

  // 폼 데이터 상태
  const [formData, setFormData] = useState({
    // 모듈 세트 폼 데이터
    moduleSetName: "",
    totalCost: "",
    imgUrls: "",
    description: "",
    options: [],

    // 모듈 폼 데이터
    moduleNfcTagId: "",
    moduleType: "",
    moduleSize: "",
    moduleCost: "",
    status: "active",
    lastMaintenanceAt: "",
    nextMaintenanceAt: "",
    currentLocation: "",
    createdAt: "",
    updatedAt: "",
  });

  // 필터 상태 (필요 시 확장 가능)
  const [filters, setFilters] = useState({
    // 모듈 세트 필터
    moduleSetSearch: "",
    moduleSetPage: 1,
    moduleSetPageSize: 10,

    // 모듈 필터
    moduleSearch: "",
    moduleStatus: "",
    modulePage: 1,
    modulePageSize: 10,
  });

  // 페이지네이션 상태
  const [moduleSetPagination, setModuleSetPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: initialDummyModuleSets.length,
    pageSize: 10,
  });

  const [modulePagination, setModulePagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: initialDummyModules.length,
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
   * 모듈 세트 목록 조회 함수
   * API 호출 시도 후 실패하면 더미 데이터를 사용
   */
  const fetchModuleSets = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/module-set/list`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          search: filters.moduleSetSearch || undefined,
          page: filters.moduleSetPage,
          pageSize: filters.moduleSetPageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setModuleSets(response.data.data.moduleSets);
        setModuleSetPagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "모듈 세트 목록을 불러오는 데 실패했습니다."
        );
        // API 호출 실패 시 더미 데이터를 사용
        setModuleSets(initialDummyModuleSets);
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError();
        // err.response.data.message ||
        //   "모듈 세트 목록을 불러오는 중 오류가 발생했습니다."
      } else {
        // setError("모듈 세트 목록을 불러오는 중 오류가 발생했습니다.");
      }
      // API 호출 실패 시 더미 데이터를 사용
      setModuleSets(initialDummyModuleSets);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 모듈 목록 조회 함수
   * API 호출 시도 후 실패하면 더미 데이터를 사용
   */
  const fetchModules = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await axios.get(`${BASE_URL}/admin/module/list`, {
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : undefined,
        },
        params: {
          search: filters.moduleSearch || undefined,
          status: filters.moduleStatus || undefined,
          page: filters.modulePage,
          pageSize: filters.modulePageSize,
        },
      });

      if (response.data.resultCode === "SUCCESS") {
        setModules(response.data.data.modules);
        setModulePagination(response.data.data.pagination);
      } else {
        setError(
          response.data.message || "모듈 목록을 불러오는 데 실패했습니다."
        );
        // API 호출 실패 시 더미 데이터를 사용
        setModules(initialDummyModules);
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        setError();
        // err.response.data.message ||
        //   "모듈 목록을 불러오는 중 오류가 발생했습니다."
      } else {
        // setError("모듈 목록을 불러오는 중 오류가 발생했습니다.");
      }
      // API 호출 실패 시 더미 데이터를 사용
      setModules(initialDummyModules);
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 모듈 세트 및 모듈 목록 조회
  useEffect(() => {
    fetchModuleSets();
    fetchModules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  // 필터 변경 핸들러
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prevFilters) => ({
      ...prevFilters,
      [name]: value,
      // 필터 변경 시 해당 페이지를 1로 리셋
      ...(name.startsWith("moduleSet") && { moduleSetPage: 1 }),
      ...(name.startsWith("module") && { modulePage: 1 }),
    }));
  };

  // 페이지 변경 핸들러
  const handlePageChange = (type, newPage) => {
    if (type === "moduleSet") {
      setFilters((prevFilters) => ({
        ...prevFilters,
        moduleSetPage: newPage,
      }));
    } else if (type === "module") {
      setFilters((prevFilters) => ({
        ...prevFilters,
        modulePage: newPage,
      }));
    }
  };

  // 모듈 세트 상세보기 클릭 시
  const handleModuleSetDetailClick = (moduleSet) => {
    setSelectedItem({ type: "moduleSet", data: moduleSet });
    setModalType("detail");
  };

  // 모듈 상세보기 클릭 시
  const handleModuleDetailClick = (module) => {
    setSelectedItem({ type: "module", data: module });
    setModalType("detail");
  };

  // 모듈 세트 수정 클릭 시
  const handleModuleSetEditClick = () => {
    if (selectedItem && selectedItem.type === "moduleSet") {
      const moduleSet = selectedItem.data;
      setFormData({
        moduleSetName: moduleSet.moduleSetName,
        totalCost: moduleSet.totalCost,
        imgUrls: moduleSet.imgUrls.join(", "),
        description: moduleSet.description,
        options: moduleSet.options,
        // 모듈 관련 필드는 초기화
        moduleNfcTagId: "",
        moduleType: "",
        moduleSize: "",
        moduleCost: "",
        status: "active",
        lastMaintenanceAt: "",
        nextMaintenanceAt: "",
        currentLocation: "",
        createdAt: "",
        updatedAt: "",
      });
      setModalType("editModuleSet");
    }
  };

  // 모듈 수정 클릭 시
  const handleModuleEditClick = () => {
    if (selectedItem && selectedItem.type === "module") {
      const module = selectedItem.data;
      setFormData({
        // 모듈 세트 관련 필드는 초기화
        moduleSetName: "",
        totalCost: "",
        imgUrls: "",
        description: "",
        options: [],
        // 모듈 관련 필드 설정
        moduleNfcTagId: module.moduleNfcTagId,
        moduleType: module.moduleType,
        moduleSize: module.moduleSize,
        moduleCost: module.moduleCost,
        status: module.status,
        lastMaintenanceAt: module.lastMaintenanceAt,
        nextMaintenanceAt: module.nextMaintenanceAt,
        currentLocation: module.currentLocation,
        createdAt: module.createdAt,
        updatedAt: module.updatedAt,
      });
      setModalType("editModule");
    }
  };

  // 모듈 세트 삭제 클릭 시
  const handleModuleSetDeleteClick = () => {
    if (selectedItem && selectedItem.type === "moduleSet") {
      setModalType("deleteModuleSet");
    }
  };

  // 모듈 삭제 클릭 시
  const handleModuleDeleteClick = () => {
    if (selectedItem && selectedItem.type === "module") {
      setModalType("deleteModule");
    }
  };

  // 신규 등록 클릭 시
  const handleAddClick = (type) => {
    if (type === "moduleSet") {
      setFormData({
        moduleSetName: "",
        totalCost: "",
        imgUrls: "",
        description: "",
        options: [],
        moduleNfcTagId: "",
        moduleType: "",
        moduleSize: "",
        moduleCost: "",
        status: "active",
        lastMaintenanceAt: "",
        nextMaintenanceAt: "",
        currentLocation: "",
        createdAt: "",
        updatedAt: "",
      });
      setModalType("addModuleSet");
    } else if (type === "module") {
      setFormData({
        moduleSetName: "",
        totalCost: "",
        imgUrls: "",
        description: "",
        options: [],
        moduleNfcTagId: "",
        moduleType: "",
        moduleSize: "",
        moduleCost: "",
        status: "active",
        lastMaintenanceAt: "",
        nextMaintenanceAt: "",
        currentLocation: "",
        createdAt: "",
        updatedAt: "",
      });
      setModalType("addModule");
    }
  };

  const closeModal = () => {
    setModalType(null);
    setSelectedItem(null);
    setFormData({
      moduleSetName: "",
      totalCost: "",
      imgUrls: "",
      description: "",
      options: [],
      moduleNfcTagId: "",
      moduleType: "",
      moduleSize: "",
      moduleCost: "",
      status: "active",
      lastMaintenanceAt: "",
      nextMaintenanceAt: "",
      currentLocation: "",
      createdAt: "",
      updatedAt: "",
    });
  };

  // 폼 변경 시
  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  /**
   * CRUD 기능 API 연동
   * 현재는 더미 데이터를 사용 중이며, API 연동 시 해당 부분을 활성화
   */

  // 모듈 세트 수정 저장 시 (더미 데이터 사용)
  const handleSaveModuleSetEditDummy = () => {
    if (selectedItem && selectedItem.type === "moduleSet") {
      setModuleSets((prevModuleSets) =>
        prevModuleSets.map((item) =>
          item.moduleSetId === selectedItem.data.moduleSetId
            ? {
                ...item,
                moduleSetName: formData.moduleSetName,
                totalCost: Number(formData.totalCost),
                imgUrls: formData.imgUrls
                  .split(",")
                  .map((url) => url.trim())
                  .filter((url) => url !== ""),
                description: formData.description,
                options: formData.options, // 필요 시 옵션 수정 로직 추가
              }
            : item
        )
      );
      closeModal();
    }
  };

  // 모듈 세트 수정 저장 시 (API 연동)
  const handleSaveModuleSetEdit = async () => {
    if (!selectedItem || selectedItem.type !== "moduleSet") return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        moduleSetName: formData.moduleSetName,
        totalCost: Number(formData.totalCost),
        imgUrls: formData.imgUrls
          .split(",")
          .map((url) => url.trim())
          .filter((url) => url !== ""),
        description: formData.description,
        // options: formData.options, // 옵션 수정 로직 필요 시 추가
      };

      const response = await axios.put(
        `${BASE_URL}/admin/module-set/update/${selectedItem.data.moduleSetId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 수정하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(
          errorMessages || "모듈 세트를 수정하는 중 오류가 발생했습니다."
        );
      } else {
        setError("모듈 세트를 수정하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModuleSets(initialDummyModuleSets);
    } finally {
      setLoading(false);
    }
  };

  // 모듈 세트 삭제 확인 시 (더미 데이터 사용)
  const handleConfirmModuleSetDeleteDummy = () => {
    if (selectedItem && selectedItem.type === "moduleSet") {
      setModuleSets((prevModuleSets) =>
        prevModuleSets.filter(
          (item) => item.moduleSetId !== selectedItem.data.moduleSetId
        )
      );
      closeModal();
    }
  };

  // 모듈 세트 삭제 확인 시 (API 연동)
  const handleConfirmModuleSetDelete = async () => {
    if (!selectedItem || selectedItem.type !== "moduleSet") return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module-set/delete/${selectedItem.data.moduleSetId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
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
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(
          errorMessages || "모듈 세트를 삭제하는 중 오류가 발생했습니다."
        );
      } else {
        setError("모듈 세트를 삭제하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModuleSets(initialDummyModuleSets);
    } finally {
      setLoading(false);
    }
  };

  // 모듈 수정 저장 시 (더미 데이터 사용)
  const handleSaveModuleEditDummy = () => {
    if (selectedItem && selectedItem.type === "module") {
      setModules((prevModules) =>
        prevModules.map((item) =>
          item.moduleId === selectedItem.data.moduleId
            ? {
                ...item,
                moduleNfcTagId: formData.moduleNfcTagId,
                moduleType: formData.moduleType,
                moduleSize: formData.moduleSize,
                moduleCost: Number(formData.moduleCost),
                status: formData.status,
                lastMaintenanceAt: formData.lastMaintenanceAt,
                nextMaintenanceAt: formData.nextMaintenanceAt,
                currentLocation: formData.currentLocation,
                updatedAt: new Date().toISOString(),
              }
            : item
        )
      );
      closeModal();
    }
  };

  // 모듈 수정 저장 시 (API 연동)
  const handleSaveModuleEdit = async () => {
    if (!selectedItem || selectedItem.type !== "module") return;
    setLoading(true);
    setError("");
    try {
      const payload = {
        moduleNfcTagId: formData.moduleNfcTagId,
        moduleType: formData.moduleType,
        moduleSize: formData.moduleSize,
        moduleCost: Number(formData.moduleCost),
        status: formData.status,
        lastMaintenanceAt: formData.lastMaintenanceAt,
        nextMaintenanceAt: formData.nextMaintenanceAt,
        currentLocation: formData.currentLocation,
      };

      const response = await axios.put(
        `${BASE_URL}/admin/module/update/${selectedItem.data.moduleId}`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 수정하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(errorMessages || "모듈을 수정하는 중 오류가 발생했습니다.");
      } else {
        setError("모듈을 수정하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModules(initialDummyModules);
    } finally {
      setLoading(false);
    }
  };

  // 모듈 삭제 확인 시 (더미 데이터 사용)
  const handleConfirmModuleDeleteDummy = () => {
    if (selectedItem && selectedItem.type === "module") {
      setModules((prevModules) =>
        prevModules.filter(
          (item) => item.moduleId !== selectedItem.data.moduleId
        )
      );
      closeModal();
    }
  };

  // 모듈 삭제 확인 시 (API 연동)
  const handleConfirmModuleDelete = async () => {
    if (!selectedItem || selectedItem.type !== "module") return;
    setLoading(true);
    setError("");
    try {
      const response = await axios.delete(
        `${BASE_URL}/admin/module/delete/${selectedItem.data.moduleId}`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 삭제하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(errorMessages || "모듈을 삭제하는 중 오류가 발생했습니다.");
      } else {
        setError("모듈을 삭제하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModules(initialDummyModules);
    } finally {
      setLoading(false);
    }
  };

  // 모듈 세트 신규 등록 저장 시 (더미 데이터 사용)
  const handleSaveModuleSetAddDummy = () => {
    const newModuleSet = {
      moduleSetId:
        moduleSets.length > 0
          ? Math.max(...moduleSets.map((ms) => ms.moduleSetId)) + 1
          : 101,
      moduleSetName: formData.moduleSetName,
      totalCost: Number(formData.totalCost),
      imgUrls: formData.imgUrls
        ? formData.imgUrls.split(",").map((url) => url.trim())
        : [],
      description: formData.description,
      options: formData.options, // 필요 시 옵션 추가 로직
    };
    setModuleSets((prevModuleSets) => [...prevModuleSets, newModuleSet]);
    closeModal();
  };

  // 모듈 세트 신규 등록 저장 시 (API 연동)
  const handleSaveModuleSetAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        moduleSetName: formData.moduleSetName,
        moduleSetDefaultOptions: formData.options, // 옵션 추가 로직 필요 시
        description: formData.description,
      };

      const response = await axios.post(
        `${BASE_URL}/admin/module-set/register`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModuleSets();
        closeModal();
      } else {
        setError(
          response.data.message || "모듈 세트를 등록하는 데 실패했습니다."
        );
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(
          errorMessages || "모듈 세트를 등록하는 중 오류가 발생했습니다."
        );
      } else {
        setError("모듈 세트를 등록하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModuleSets(initialDummyModuleSets);
    } finally {
      setLoading(false);
    }
  };

  // 모듈 신규 등록 저장 시 (더미 데이터 사용)
  const handleSaveModuleAddDummy = () => {
    const newModule = {
      moduleId:
        modules.length > 0
          ? Math.max(...modules.map((m) => m.moduleId)) + 1
          : 1,
      moduleNfcTagId: formData.moduleNfcTagId,
      moduleType: formData.moduleType,
      moduleSize: formData.moduleSize,
      moduleCost: Number(formData.moduleCost),
      status: formData.status,
      lastMaintenanceAt: formData.lastMaintenanceAt,
      nextMaintenanceAt: formData.nextMaintenanceAt,
      currentLocation: formData.currentLocation,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setModules((prevModules) => [...prevModules, newModule]);
    closeModal();
  };

  // 모듈 신규 등록 저장 시 (API 연동)
  const handleSaveModuleAdd = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        moduleNfcTagId: formData.moduleNfcTagId,
        moduleType: formData.moduleType,
        moduleSize: formData.moduleSize,
        moduleCost: Number(formData.moduleCost),
      };

      const response = await axios.post(
        `${BASE_URL}/admin/module/register`,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: token ? `Bearer ${token}` : undefined,
          },
        }
      );

      if (response.data.resultCode === "SUCCESS") {
        fetchModules();
        closeModal();
      } else {
        setError(response.data.message || "모듈을 등록하는 데 실패했습니다.");
      }
    } catch (err) {
      console.error(err);
      if (err.response && err.response.data) {
        const errorMessages = err.response.data.errors
          ? err.response.data.errors
              .map((error) => `${error.field}: ${error.message}`)
              .join(", ")
          : err.response.data.message;
        setError(errorMessages || "모듈을 등록하는 중 오류가 발생했습니다.");
      } else {
        setError("모듈을 등록하는 중 오류가 발생했습니다.");
      }
      // API 연동 실패 시 더미 데이터를 사용하도록 설정
      setModules(initialDummyModules);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="module-container">
      <div className="module-header">
        <h1>모듈 관리</h1>
        <div>
          <button
            className="add-button"
            onClick={() => handleAddClick("moduleSet")}
          >
            모듈 세트 등록
          </button>
          <button
            className="add-button"
            onClick={() => handleAddClick("module")}
          >
            모듈 등록
          </button>
        </div>
      </div>

      {/* 필터링 섹션 (모듈 세트) */}
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
        <button onClick={() => fetchModuleSets()}>검색</button>
      </div>

      {/* 모듈 세트 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <table className="module-set-table">
            <thead>
              <tr>
                <th>모듈 세트 ID</th>
                <th>모듈 세트 이름</th>
                <th>총 가격 (원)</th>
                <th>이미지</th>
                <th>설명</th>
                <th>포함된 옵션</th>
                <th>상세 보기</th>
              </tr>
            </thead>
            <tbody>
              {moduleSets.length > 0 ? (
                moduleSets.map((set) => (
                  <tr key={set.moduleSetId}>
                    <td>{set.moduleSetId}</td>
                    <td>{set.moduleSetName}</td>
                    <td>{set.totalCost.toLocaleString()}원</td>
                    <td>
                      {set.imgUrls.length > 0 ? (
                        set.imgUrls.map((url, index) => (
                          <img
                            key={index}
                            src={url}
                            alt={`${set.moduleSetName} 이미지 ${index + 1}`}
                            className="module-set-image"
                          />
                        ))
                      ) : (
                        <span>이미지 없음</span>
                      )}
                    </td>
                    <td>{set.description}</td>
                    <td>
                      {set.options.length > 0 ? (
                        <ul>
                          {set.options.map((option) => (
                            <li key={option.optionId}>
                              {option.optionName} x {option.quantity}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <span>옵션 없음</span>
                      )}
                    </td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => handleModuleSetDetailClick(set)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">조회된 모듈 세트가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>

          {/* 모듈 세트 페이지네이션 */}
          <div className="pagination">
            <button
              onClick={() =>
                handlePageChange("moduleSet", filters.moduleSetPage - 1)
              }
              disabled={filters.moduleSetPage === 1}
            >
              이전
            </button>
            <span>
              {filters.moduleSetPage} / {moduleSetPagination.totalPages}
            </span>
            <button
              onClick={() =>
                handlePageChange("moduleSet", filters.moduleSetPage + 1)
              }
              disabled={
                filters.moduleSetPage === moduleSetPagination.totalPages
              }
            >
              다음
            </button>
          </div>
        </>
      )}

      {/* 필터링 섹션 (모듈) */}
      <div className="filters">
        <h2>모듈 목록</h2>
        <label>
          상태
          <select
            name="moduleStatus"
            value={filters.moduleStatus}
            onChange={handleFilterChange}
          >
            <option value="">전체</option>
            <option value="active">활성화</option>
            <option value="inactive">비활성화</option>
            <option value="maintenance">정비 중</option>
          </select>
        </label>
        <label>
          검색
          <input
            type="text"
            name="moduleSearch"
            value={filters.moduleSearch}
            onChange={handleFilterChange}
            placeholder="모듈 NFC 태그 ID 또는 타입 검색"
          />
        </label>
        <button onClick={() => fetchModules()}>검색</button>
      </div>

      {/* 모듈 목록 테이블 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <>
          {error && <p className="error">{error}</p>}
          <table className="module-table">
            <thead>
              <tr>
                <th>모듈 ID</th>
                <th>NFC 태그 ID</th>
                <th>모듈 타입</th>
                <th>모듈 크기</th>
                <th>모듈 비용 (원)</th>
                <th>상태</th>
                <th>현재 위치</th>
                <th>등록 일자</th>
                <th>수정 일자</th>
                <th>상세 보기</th>
              </tr>
            </thead>
            <tbody>
              {modules.length > 0 ? (
                modules.map((module) => (
                  <tr key={module.moduleId}>
                    <td>{module.moduleId}</td>
                    <td>{module.moduleNfcTagId}</td>
                    <td>{module.moduleType}</td>
                    <td>{module.moduleSize}</td>
                    <td>{module.moduleCost.toLocaleString()}원</td>
                    <td>
                      {module.status === "active"
                        ? "활성화"
                        : module.status === "inactive"
                        ? "비활성화"
                        : "정비 중"}
                    </td>
                    <td>{module.currentLocation || "미정"}</td>
                    <td>{new Date(module.createdAt).toLocaleString()}</td>
                    <td>{new Date(module.updatedAt).toLocaleString()}</td>
                    <td>
                      <button
                        className="detail-button"
                        onClick={() => handleModuleDetailClick(module)}
                      >
                        <MdSearch />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10">조회된 모듈이 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>

          {/* 모듈 페이지네이션 */}
          <div className="pagination">
            <button
              onClick={() => handlePageChange("module", filters.modulePage - 1)}
              disabled={filters.modulePage === 1}
            >
              이전
            </button>
            <span>
              {filters.modulePage} / {modulePagination.totalPages}
            </span>
            <button
              onClick={() => handlePageChange("module", filters.modulePage + 1)}
              disabled={filters.modulePage === modulePagination.totalPages}
            >
              다음
            </button>
          </div>
        </>
      )}

      {/* 모달 */}
      <Modal isOpen={modalType !== null} onClose={closeModal}>
        {modalType === "detail" && selectedItem && (
          <div className="detail-content">
            {selectedItem.type === "moduleSet" ? (
              <>
                <h2>모듈 세트 상세 정보</h2>
                <p>모듈 세트 ID: {selectedItem.data.moduleSetId}</p>
                <p>모듈 세트 이름: {selectedItem.data.moduleSetName}</p>
                <p>총 가격: {selectedItem.data.totalCost.toLocaleString()}원</p>
                <p>이미지:</p>
                {selectedItem.data.imgUrls.length > 0 ? (
                  selectedItem.data.imgUrls.map((url, index) => (
                    <img
                      key={index}
                      src={url}
                      alt={`${selectedItem.data.moduleSetName} 이미지 ${
                        index + 1
                      }`}
                      className="module-set-image"
                    />
                  ))
                ) : (
                  <p>이미지 없음</p>
                )}
                <p>설명: {selectedItem.data.description}</p>
                <p>포함된 옵션:</p>
                {selectedItem.data.options.length > 0 ? (
                  <ul>
                    {selectedItem.data.options.map((option) => (
                      <li key={option.optionId}>
                        {option.optionName} x {option.quantity}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>옵션 없음</p>
                )}
                <div className="modal-actions">
                  <button
                    onClick={handleModuleSetEditClick}
                    className="edit-button"
                  >
                    수정
                  </button>
                  <button
                    onClick={handleModuleSetDeleteClick}
                    className="delete-button"
                  >
                    삭제
                  </button>
                </div>
              </>
            ) : selectedItem.type === "module" ? (
              <>
                <h2>모듈 상세 정보</h2>
                <p>모듈 ID: {selectedItem.data.moduleId}</p>
                <p>NFC 태그 ID: {selectedItem.data.moduleNfcTagId}</p>
                <p>모듈 타입: {selectedItem.data.moduleType}</p>
                <p>모듈 크기: {selectedItem.data.moduleSize}</p>
                <p>
                  모듈 비용: {selectedItem.data.moduleCost.toLocaleString()}원
                </p>
                <p>
                  상태:{" "}
                  {selectedItem.data.status === "active"
                    ? "활성화"
                    : selectedItem.data.status === "inactive"
                    ? "비활성화"
                    : "정비 중"}
                </p>
                <p>현재 위치: {selectedItem.data.currentLocation || "미정"}</p>
                <p>
                  등록 일자:{" "}
                  {new Date(selectedItem.data.createdAt).toLocaleString()}
                </p>
                <p>
                  수정 일자:{" "}
                  {new Date(selectedItem.data.updatedAt).toLocaleString()}
                </p>
                <p>
                  최근 정비 일자:{" "}
                  {selectedItem.data.lastMaintenanceAt || "없음"}
                </p>
                <p>
                  다음 정비 일자:{" "}
                  {selectedItem.data.nextMaintenanceAt || "없음"}
                </p>
                <div className="modal-actions">
                  <button
                    onClick={handleModuleEditClick}
                    className="edit-button"
                  >
                    수정
                  </button>
                  <button
                    onClick={handleModuleDeleteClick}
                    className="delete-button"
                  >
                    삭제
                  </button>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* 수정 모달 */}
        {(modalType === "editModuleSet" || modalType === "editModule") && (
          <div className="edit-content">
            <h2>
              {modalType === "editModuleSet" ? "모듈 세트 수정" : "모듈 수정"}
            </h2>
            <form className="edit-form">
              {modalType === "editModuleSet" ? (
                <>
                  <label>
                    모듈 세트 이름:
                    <input
                      type="text"
                      name="moduleSetName"
                      value={formData.moduleSetName}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    총 가격 (원):
                    <input
                      type="number"
                      name="totalCost"
                      value={formData.totalCost}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    이미지 URL 목록 (콤마로 구분):
                    <input
                      type="text"
                      name="imgUrls"
                      value={formData.imgUrls}
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
                  {/* 옵션 수정 로직 필요 시 추가 */}
                </>
              ) : (
                <>
                  <label>
                    NFC 태그 ID:
                    <input
                      type="text"
                      name="moduleNfcTagId"
                      value={formData.moduleNfcTagId}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 타입:
                    <input
                      type="text"
                      name="moduleType"
                      value={formData.moduleType}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 크기:
                    <input
                      type="text"
                      name="moduleSize"
                      value={formData.moduleSize}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 비용 (원):
                    <input
                      type="number"
                      name="moduleCost"
                      value={formData.moduleCost}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    상태:
                    <select
                      name="status"
                      value={formData.status}
                      onChange={handleFormChange}
                    >
                      <option value="active">활성화</option>
                      <option value="inactive">비활성화</option>
                      <option value="maintenance">정비 중</option>
                    </select>
                  </label>
                  <label>
                    최근 정비 일자:
                    <input
                      type="date"
                      name="lastMaintenanceAt"
                      value={formData.lastMaintenanceAt}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    다음 정비 일자:
                    <input
                      type="date"
                      name="nextMaintenanceAt"
                      value={formData.nextMaintenanceAt}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    현재 위치:
                    <input
                      type="text"
                      name="currentLocation"
                      value={formData.currentLocation}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    등록 일자:
                    <input
                      type="datetime-local"
                      name="createdAt"
                      value={formData.createdAt}
                      onChange={handleFormChange}
                      disabled
                    />
                  </label>
                  <label>
                    수정 일자:
                    <input
                      type="datetime-local"
                      name="updatedAt"
                      value={formData.updatedAt}
                      onChange={handleFormChange}
                      disabled
                    />
                  </label>
                </>
              )}
            </form>
            <div className="modal-actions">
              {modalType === "editModuleSet" ? (
                <>
                  {/* 더미 데이터 수정 저장 */}
                  {/* <button onClick={handleSaveModuleSetEditDummy} className="save-button" disabled={loading}>
                    저장
                  </button> */}

                  {/* API 연동 수정 저장 */}
                  <button
                    onClick={handleSaveModuleSetEdit}
                    className="save-button"
                    disabled={loading}
                  >
                    저장
                  </button>
                </>
              ) : (
                <>
                  {/* 더미 데이터 수정 저장 */}
                  {/* <button onClick={handleSaveModuleEditDummy} className="save-button" disabled={loading}>
                    저장
                  </button> */}

                  {/* API 연동 수정 저장 */}
                  <button
                    onClick={handleSaveModuleEdit}
                    className="save-button"
                    disabled={loading}
                  >
                    저장
                  </button>
                </>
              )}
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {/* 삭제 확인 모달 */}
        {(modalType === "deleteModuleSet" || modalType === "deleteModule") && (
          <div className="delete-content">
            <h2>
              {modalType === "deleteModuleSet"
                ? "모듈 세트 삭제 확인"
                : "모듈 삭제 확인"}
            </h2>
            <p>
              {modalType === "deleteModuleSet"
                ? "정말로 이 모듈 세트를 삭제하시겠습니까?"
                : "정말로 이 모듈을 삭제하시겠습니까?"}
            </p>
            <div className="modal-actions">
              {modalType === "deleteModuleSet" ? (
                <>
                  {/* 더미 데이터 삭제 */}
                  <button
                    onClick={handleConfirmModuleSetDeleteDummy}
                    className="confirm-delete-button"
                    disabled={loading}
                  >
                    삭제
                  </button>

                  {/* API 연동 삭제 */}
                  {/* <button
                    onClick={handleConfirmModuleSetDelete}
                    className="confirm-delete-button"
                    disabled={loading}
                  >
                    삭제
                  </button> */}
                </>
              ) : (
                <>
                  {/* 더미 데이터 삭제 */}
                  <button
                    onClick={handleConfirmModuleDeleteDummy}
                    className="confirm-delete-button"
                    disabled={loading}
                  >
                    삭제
                  </button>

                  {/* API 연동 삭제 */}
                  {/* <button
                    onClick={handleConfirmModuleDelete}
                    className="confirm-delete-button"
                    disabled={loading}
                  >
                    삭제
                  </button> */}
                </>
              )}
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}

        {/* 신규 등록 모달 */}
        {(modalType === "addModuleSet" || modalType === "addModule") && (
          <div className="add-content">
            <h2>
              {modalType === "addModuleSet" ? "모듈 세트 등록" : "모듈 등록"}
            </h2>
            <form className="add-form">
              {modalType === "addModuleSet" ? (
                // 모듈 세트 등록 폼
                <>
                  <label>
                    모듈 세트 이름:
                    <input
                      type="text"
                      name="moduleSetName"
                      value={formData.moduleSetName}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    총 가격 (원):
                    <input
                      type="number"
                      name="totalCost"
                      value={formData.totalCost}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    이미지 URL 목록 (콤마로 구분):
                    <input
                      type="text"
                      name="imgUrls"
                      value={formData.imgUrls}
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
                  {/* 옵션 추가 로직 필요 시 추가 */}
                </>
              ) : (
                // 모듈 등록 폼
                <>
                  <label>
                    NFC 태그 ID:
                    <input
                      type="text"
                      name="moduleNfcTagId"
                      value={formData.moduleNfcTagId}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 타입:
                    <input
                      type="text"
                      name="moduleType"
                      value={formData.moduleType}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 크기:
                    <input
                      type="text"
                      name="moduleSize"
                      value={formData.moduleSize}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    모듈 비용 (원):
                    <input
                      type="number"
                      name="moduleCost"
                      value={formData.moduleCost}
                      onChange={handleFormChange}
                      required
                    />
                  </label>
                  <label>
                    상태:
                    <select
                      name="status"
                      value={formData.status}
                      onChange={handleFormChange}
                    >
                      <option value="active">활성화</option>
                      <option value="inactive">비활성화</option>
                      <option value="maintenance">정비 중</option>
                    </select>
                  </label>
                  <label>
                    최근 정비 일자:
                    <input
                      type="date"
                      name="lastMaintenanceAt"
                      value={formData.lastMaintenanceAt}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    다음 정비 일자:
                    <input
                      type="date"
                      name="nextMaintenanceAt"
                      value={formData.nextMaintenanceAt}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    현재 위치:
                    <input
                      type="text"
                      name="currentLocation"
                      value={formData.currentLocation}
                      onChange={handleFormChange}
                    />
                  </label>
                  <label>
                    등록 일자:
                    <input
                      type="datetime-local"
                      name="createdAt"
                      value={formData.createdAt}
                      onChange={handleFormChange}
                      disabled
                    />
                  </label>
                  <label>
                    수정 일자:
                    <input
                      type="datetime-local"
                      name="updatedAt"
                      value={formData.updatedAt}
                      onChange={handleFormChange}
                      disabled
                    />
                  </label>
                </>
              )}
            </form>
            <div className="modal-actions">
              {modalType === "addModuleSet" ? (
                <>
                  {/* 더미 데이터 신규 등록 저장 */}
                  <button
                    onClick={handleSaveModuleSetAddDummy}
                    className="save-button"
                    disabled={loading}
                  >
                    등록
                  </button>

                  {/* API 연동 신규 등록 저장 */}
                  {/* <button
                    onClick={handleSaveModuleSetAdd}
                    className="save-button"
                    disabled={loading}
                  >
                    등록
                  </button> */}
                </>
              ) : (
                <>
                  {/* 더미 데이터 신규 등록 저장 */}
                  <button
                    onClick={handleSaveModuleAddDummy}
                    className="save-button"
                    disabled={loading}
                  >
                    등록
                  </button>

                  {/* API 연동 신규 등록 저장 */}
                  {/* <button
                    onClick={handleSaveModuleAdd}
                    className="save-button"
                    disabled={loading}
                  >
                    등록
                  </button> */}
                </>
              )}
              <button onClick={closeModal} className="cancel-button">
                취소
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}

export default ModuleManagement;

import React, { useEffect, useState, useCallback } from "react"
import axios from "axios"
import "./ModuleSetList.css"
import { useNavigate } from "react-router-dom"

function ModuleSetList() {
  const [isNavigating, setIsNavigating] = useState(false) // 네비게이션 로딩 상태 추가
  const [loadingText, setLoadingText] = useState("모듈 초기화 중...")

  const [moduleSets, setModuleSets] = useState([])
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 100,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedModule, setSelectedModule] = useState(null)
  const [showModal, setShowModal] = useState(false)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)

  const navigate = useNavigate()
  // const API_URL = `https://backend-wandering-river-6835.fly.dev/user/module-sets`

  const fetchModuleSets = useCallback(
    async (page, size) => {
      setLoading(true)
      setError(null)

      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/module-sets`, {
          params: { page, page_size: size },
        })

        if (response.data.resultCode === "SUCCESS") {
          setModuleSets(response.data.data.moduleSets)
          setPagination(response.data.data.pagination)
        } else {
          setError(response.data.message)
          setModuleSets([])
        }
      } catch (err) {
        setError("An unexpected error occurred. Please try again later.")
        console.error(err)
      } finally {
        setLoading(false)
      }
    },
    []
  )

  useEffect(() => {
    fetchModuleSets(pagination.currentPage, pagination.pageSize)
  }, [fetchModuleSets, pagination.currentPage, pagination.pageSize])

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= pagination.totalPages) {
      setPagination((prev) => ({ ...prev, currentPage: newPage }))
    }
  }

  const handleSelectModule = (module) => {
    setSelectedModule(module)
    setCurrentImageIndex(0)
    setShowModal(true)
  }

  const handleNextStep = async () => {
    setIsNavigating(true)
    try {
      sessionStorage.setItem("ModuleSet", JSON.stringify(selectedModule))

      // 로딩 텍스트 변경을 위한 타이머 설정
      setTimeout(() => setLoadingText("모듈 나사 박는중..."), 2000)
      setTimeout(() => setLoadingText("모듈 장착 하는중..."), 5000)
      setTimeout(() => setLoadingText("모듈 조립 완료!"), 9500)

      await new Promise((resolve) => setTimeout(resolve, 10000))
      navigate("/option_select", { state: { selectedModule } })
    } catch (error) {
      console.error("Navigation error:", error)
    } finally {
      setIsNavigating(false)
      setLoadingText("모듈 조립하러 가는중...") // 초기 텍스트로 리셋
    }
  }

  return (
    <div className="module-list-container">
      {loading && <div className="loading">Loading...</div>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && (
        <>
          <div className="module-grid">
            {moduleSets.map((moduleSet) => (
              <div key={moduleSet.moduleSetId} className="module-card" onClick={() => handleSelectModule(moduleSet)}>
                <img src={moduleSet.imgUrls[0]} alt={moduleSet.moduleSetName} />
                {/* <img src="./예시.png" alt="" /> */}
                <h4>{moduleSet.moduleSetName}</h4>
              </div>
            ))}
          </div>
        </>
      )}

      {showModal && selectedModule && (
        <div className="module-set-card-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="module-set-card-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="module-set-modal-header">
              <h2>{selectedModule.moduleSetName}</h2>
              <button className="module-set-modal-close-button" onClick={() => setShowModal(false)}>
                창 닫기
              </button>
            </div>

            <div className="module-set-modal-body">
              <img src={selectedModule.imgUrls[0]} alt={`${selectedModule.moduleSetName} - 이미지 ${currentImageIndex + 1}`} />
           
              <div className="module-modal-details">
                <div className="module-modal-description">
                  <h3>상세 설명</h3>
                  <p>{selectedModule.description}</p>
                </div>

                <div className="modal-module-options">
                  <h3>포함된 옵션</h3>
                  <ul>
                    {selectedModule.moduleSetOptionTypes.map((option) => (
                      <li key={option.optionTypeId}>
                        {option.optionTypeName} (수량: {option.quantity})
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="modal-total-cost-container">
                  <h3>렌트 비용: {selectedModule.basePrice.toLocaleString()}원</h3>
                </div>
              </div>
              <button onClick={handleNextStep} className="module-set-modal-next-button">
                다음 단계 →
              </button>
            </div>
          </div>
        </div>
      )}
      {/* 네비게이션 로딩 오버레이 */}
      {isNavigating && (
        <div className="loading-overlay">
          <div className="loading-container">
            <img src="/moduleloading.gif" alt="로딩 중..." className="loading-image" />
            <div className="loading-text">{loadingText}</div>
            <div className="loading-progress">
              <div className="loading-progress-bar"></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ModuleSetList

import React, { useState, useEffect } from "react"
import axios from "axios"
import { useNavigate, useLocation } from "react-router-dom"
import "./option_Select.css"

const OptionDetailsModal = ({ option, onClose }) => {
  if (!option) return null

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        <img src={option.imgUrls[0]} alt={option.optionTypeName} className="modal-image" />
       
        <h2>{option.optionTypeName}</h2>
        <div className="modal-details">
          <p>
            <strong>설명:</strong> {option.description}
          </p>
          <p>
            <strong>크기:</strong> {option.optionTypeSize}
          </p>
          <p>
            <strong>가격:</strong> {option.optionTypeCost.toLocaleString()}원
          </p>
          <p>
            <strong>재고:</strong> {option.stockQuantity}개
          </p>
        </div>
      </div>
    </div>
  )
}

const ExistOptionsPage = () => {
  const [showScroll, setShowScroll] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const moduleSetcarString = sessionStorage.getItem("ModuleSet")
  const moduleSetcar = JSON.parse(moduleSetcarString)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedOptions, setSelectedOptions] = useState([])
  const [allOptions, setAllOptions] = useState([])
  const [unselectedOptions, setUnselectedOptions] = useState([])
  const [selectedOptionDetails, setSelectedOptionDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [activeTab, setActiveTab] = useState("selected")

  const fetchCompleteOptionData = async () => {
    setLoading(true)
    try {
      const firstResponse = await axios.get(`${import.meta.env.VITE_API_URL}/user/option-types`, {
        params: {
          page: 1,
          page_size: 100,
        },
      })
      console.log(firstResponse)

      const { totalPages } = firstResponse.data.data.pagination
      let allOptionTypes = []

      for (let page = 1; page <= totalPages; page++) {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/user/option-types`, {
          params: {
            page: page,
            page_size: 100,
          },
        })

        allOptionTypes = [...allOptionTypes, ...response.data.data.optionTypes]
      }
      const existingOptions = location.state?.existingOptions || []
      const moduleOptions = location.state?.selectedModule?.moduleSetOptionTypes || []
      const selectedOptionData = existingOptions.length > 0 ? existingOptions : moduleOptions

      const completeSelectedOptions = selectedOptionData
        .map((selectedItem) => {
          const fullOptionDetails = allOptionTypes.find((option) => option.optionTypeId === selectedItem.optionTypeId)

          return {
            ...fullOptionDetails,
            quantity: selectedItem.quantity || 1,
          }
        })
        .filter(Boolean)

      const completeUnselectedOptions = allOptionTypes.filter((option) => !completeSelectedOptions.some((selected) => selected.optionTypeId === option.optionTypeId))
      setSelectedOptions(completeSelectedOptions)
      setAllOptions(allOptionTypes)
      setUnselectedOptions(completeUnselectedOptions)
    } catch (err) {
      setError("옵션 정보를 가져오는 중 오류가 발생했습니다.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  useEffect(() => {
    const checkScrollTop = () => {
      if (!showScroll && window.pageYOffset > 400) {
        setShowScroll(true)
      } else if (showScroll && window.pageYOffset <= 400) {
        setShowScroll(false)
      }
    }
    window.addEventListener("scroll", checkScrollTop)
    return () => window.removeEventListener("scroll", checkScrollTop)
  }, [showScroll])
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  }
  useEffect(() => {
    fetchCompleteOptionData()
  }, [])

  const addOptionToSelected = (option) => {
    setSelectedOptions([...selectedOptions, { ...option, quantity: 1 }])
    setUnselectedOptions(unselectedOptions.filter((opt) => opt.optionTypeId !== option.optionTypeId))
  }

  const removeOptionFromSelected = (optionToRemove) => {
    const updatedSelectedOptions = selectedOptions.filter((opt) => opt.optionTypeId !== optionToRemove.optionTypeId)
    setSelectedOptions(updatedSelectedOptions)
    setUnselectedOptions([...unselectedOptions, optionToRemove])
  }

  const updateQuantity = (optionId, change) => {
    const updatedOptions = selectedOptions.map((option) => {
      if (option.optionTypeId === optionId) {
        const newQuantity = Math.max(0, (option.quantity || 0) + change)
        return {
          ...option,
          quantity: newQuantity,
        }
      }
      return option
    })

    const optionToMove = updatedOptions.find((option) => option.optionTypeId === optionId && option.quantity === 0)

    if (optionToMove) {
      const filteredOptions = updatedOptions.filter((option) => option.optionTypeId !== optionId)
      setSelectedOptions(filteredOptions)
      setUnselectedOptions([...unselectedOptions, { ...optionToMove, quantity: 1 }])
    } else {
      setSelectedOptions(updatedOptions)
    }
  }

  const goToPreviousPage = () => {
    navigate("/ModuleSetList")
  }

  const goToNextPage = () => {
    const optionData = {
      selectedOptions: selectedOptions.map((option) => ({
        optionTypeId: option.optionTypeId,
        quantity: option.quantity,
      })),
    }
    sessionStorage.setItem("selectedOptionData", JSON.stringify(optionData))
    navigate("/rentForm")
  }

  if (loading) return <div>로딩 중...</div>
  if (error) return <div>{error}</div>

  return (
    <div className="custom-container">
      <div className="vehicle-image">
        <h1 className="custom-heading">{moduleSetcar.moduleSetName} 차량</h1>
        <h3 className="custom-subheading">{moduleSetcar.description}</h3>
        <img src="./pbvcarsi.gif" alt="Vehicle" />
      </div>

      <div className="option-select-container">
        {selectedOptionDetails && <OptionDetailsModal option={selectedOptionDetails} onClose={() => setSelectedOptionDetails(null)} />}

        <div className="tabs">
          <div className={`tab ${activeTab === "selected" ? "active" : ""}`} onClick={() => setActiveTab("selected")}>
            선택된 옵션
          </div>
          <div className={`tab ${activeTab === "unselected" ? "active" : ""}`} onClick={() => setActiveTab("unselected")}>
            미선택 옵션
          </div>
        </div>

        {activeTab === "selected" && (
          <div className="options-section">
            <div className="custom-grid">
              {selectedOptions.map((option) => (
                <div key={option.optionTypeId} className="custom-card" onClick={() => setSelectedOptionDetails(option)}>
                  <div className="custom-info">
                    <img src={option.imgUrls[0]} alt={option.optionTypeName} className="custom-image" />
                    
                    <div className="custom-details">
                      <h3>{option.optionTypeName}</h3>
                      <p>{option.description}</p>
                    </div>
                  </div>
                  <div className="custom-actions">
                    <div className="quantity-control">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          updateQuantity(option.optionTypeId, -1)
                        }}
                      >
                        -
                      </button>
                      <span>{option.quantity}</span>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          updateQuantity(option.optionTypeId, 1)
                        }}
                      >
                        +
                      </button>
                    </div>
                    <button
                      className="custom-button"
                      onClick={(e) => {
                        e.stopPropagation()
                        removeOptionFromSelected(option)
                      }}
                    >
                      제거
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === "unselected" && (
          <div className="options-section">
            <div className="selected-tags">
              {selectedOptions.map((option) => (
                <div key={option.optionTypeId} className="option-tag">
                  <span>{option.optionTypeName}</span>
                  <button onClick={() => removeOptionFromSelected(option)} className="tag-remove-btn">
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div className="search-container">
              <div className="search-input-wrapper">
                <input type="text" placeholder="옵션 검색" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="search-input" />
                {searchTerm && (
                  <button className="search-clear-button" onClick={() => setSearchTerm("")}>
                    ×
                  </button>
                )}
              </div>
            </div>
            <div className="custom-grid">
              {unselectedOptions
                .filter((option) => option.optionTypeName.toLowerCase().includes(searchTerm.toLowerCase()) || option.description.toLowerCase().includes(searchTerm.toLowerCase()))
                .map((option) => (
                  <div key={option.optionTypeId} className="custom-card" onClick={() => setSelectedOptionDetails(option)}>
                    <div className="custom-info">
                      <img src={option.imgUrls[0]} alt={option.optionTypeName} className="custom-image" />
                      <div className="custom-details">
                        <h3>{option.optionTypeName}</h3>
                        <p>{option.description}</p>
                        <p>가격: {option.optionTypeCost.toLocaleString()}원</p>
                      </div>
                    </div>
                    <div className="custom-actions-plus">
                      <button
                        className="custom-button"
                        onClick={(e) => {
                          e.stopPropagation()
                          addOptionToSelected(option)
                        }}
                      >
                        추가
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        <div className="navigation-buttons">
          <button onClick={goToPreviousPage} className="custom-preview-button">
            이전 페이지로 돌아가기
          </button>
          <button onClick={goToNextPage} className="custom-next-button">
            다음 페이지로 이동하기
          </button>
        </div>
      </div>
      <button className={`scroll-to-top ${showScroll ? "visible" : ""}`} onClick={scrollToTop}>
        ↑
      </button>
    </div>
  )
}

export default ExistOptionsPage

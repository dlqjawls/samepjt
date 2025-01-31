import React, { useState, useEffect } from "react"
import axios from "axios"
import { useNavigate, useLocation } from "react-router-dom"
import "./option_Select.css"

const OptionDetailsModal = ({ option, onClose }) => {
  if (!option) return null

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
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
            <strong>가격:</strong> {option.optionTypeCost}원
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
  const location = useLocation()
  const navigate = useNavigate()

  const [selectedOptions, setSelectedOptions] = useState([])
  const [allOptions, setAllOptions] = useState([])
  const [unselectedOptions, setUnselectedOptions] = useState([])
  const [selectedOptionDetails, setSelectedOptionDetails] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const fetchCompleteOptionData = async () => {
    setLoading(true)
    try {
      const firstResponse = await axios.get("https://backend-wandering-river-6835.fly.dev/user/option-types", {
        params: {
          page: 1,
          page_size: 10,
        },
      })
      console.log(firstResponse)

      const { totalPages } = firstResponse.data.data.pagination
      let allOptionTypes = []

      for (let page = 1; page <= totalPages; page++) {
        const response = await axios.get("https://backend-wandering-river-6835.fly.dev/user/option-types", {
          params: {
            page: page,
            page_size: 10,
          },
        })

        allOptionTypes = [...allOptionTypes, ...response.data.data.optionTypes]
      }

      const selectedOptionData = location.state?.selectedModule?.moduleSetOptionTypes || []

      const completeSelectedOptions = selectedOptionData.map((selectedItem) => {
        const fullOptionDetails = allOptionTypes.find((option) => option.optionTypeId === selectedItem.optionTypeId)

        return {
          ...fullOptionDetails,
          quantity: selectedItem.quantity || 1,
        }
      })

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
        return {
          ...option,
          quantity: Math.max(0, (option.quantity || 0) + change),
        }
      }
      return option
    })

    setSelectedOptions(updatedOptions)
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
      {selectedOptionDetails && <OptionDetailsModal option={selectedOptionDetails} onClose={() => setSelectedOptionDetails(null)} />}

      <div className="options-section">
        <h2>선택된 옵션</h2>
        <div className="custom-grid">
          {selectedOptions.map((option) => (
            <div key={option.optionTypeId} className="custom-row">
              <div className="custom-info">
                <img src={option.imgUrls[0]} alt={option.optionTypeName} className="custom-image" />
                <div className="custom-details">
                  <h3>{option.optionTypeName}</h3>
                  <p>{option.description}</p>
                </div>
              </div>
              <div className="custom-actions">
                <button onClick={() => setSelectedOptionDetails(option)}>상세 정보</button>
                <div className="quantity-control">
                  <button onClick={() => updateQuantity(option.optionTypeId, -1)}>-</button>
                  <span>{option.quantity}</span>
                  <button onClick={() => updateQuantity(option.optionTypeId, 1)}>+</button>
                </div>
                <button onClick={() => removeOptionFromSelected(option)}>제거</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="options-section">
        <h2>미선택 옵션</h2>
        <div className="custom-grid">
          {unselectedOptions.map((option) => (
            <div key={option.optionTypeId} className="custom-row">
              <div className="custom-info">
                <img src={option.imgUrls[0]} alt={option.optionTypeName} className="custom-image" />
                <div className="custom-details">
                  <h3>{option.optionTypeName}</h3>
                  <p>{option.description}</p>
                  <p>가격: {option.optionTypeCost}원</p>
                </div>
              </div>
              <div className="custom-actions">
                <button onClick={() => setSelectedOptionDetails(option)}>상세 정보</button>
                <button onClick={() => addOptionToSelected(option)}>추가</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="navigation-buttons">
        <button onClick={goToPreviousPage} className="custom-next-button">
          이전 페이지로 돌아가기
        </button>
        <button onClick={goToNextPage} className="custom-next-button">
          다음 페이지로 이동하기
        </button>
      </div>
    </div>
  )
}

export default ExistOptionsPage

import React, { useState, useEffect } from "react"
import axios from "axios"

const OptionsPage = () => {
  const [options, setOptions] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [totalPages, setTotalPages] = useState(1)
  const [searchOptionId, setSearchOptionId] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const fetchOptions = async () => {
    setLoading(true)
    setError("")
    try {
      const response = await axios.get("https://backend-wandering-river-6835.fly.dev/user/option-types", {
        params: {
          page: currentPage,
          page_size: pageSize,
          option_id: searchOptionId || undefined,
        },
      })
      const { options, pagination } = response.data.data
      setOptions(options)
      setTotalPages(pagination.totalPages)
    } catch (err) {
      setError("옵션 목록을 가져오는 중 오류가 발생했습니다.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOptions()
  }, [currentPage, pageSize])

  const handleSearch = () => {
    setCurrentPage(1) // 검색 시 페이지 번호를 1로 초기화
    fetchOptions()
  }

  return (
    <div>
      <h1>옵션 목록</h1>
      <div>
        <label>
          옵션 ID 검색:
          <input type="text" value={searchOptionId} onChange={(e) => setSearchOptionId(e.target.value)} placeholder="옵션 ID 입력" />
        </label>
        <button onClick={handleSearch}>검색</button>
      </div>
      <div>
        <label>
          페이지 크기:
          <select value={pageSize} onChange={(e) => setPageSize(Number(e.target.value))}>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={30}>30</option>
          </select>
        </label>
      </div>
      {loading ? (
        <p>로딩 중...</p>
      ) : error ? (
        <p>{error}</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>옵션 ID</th>
              <th>옵션 이름</th>
              <th>크기</th>
              <th>가격</th>
              <th>유형</th>
              <th>재고</th>
              <th>이미지</th>
              <th>설명</th>
            </tr>
          </thead>
          <tbody>
            {options.map((option) => (
              <tr key={option.optionId}>
                <td>{option.optionId}</td>
                <td>{option.optionName}</td>
                <td>{option.optionSize}</td>
                <td>{option.optionCost}</td>
                <td>{option.optionType}</td>
                <td>{option.stockQuantity}</td>
                <td>
                  {option.imgUrls.map((url, idx) => (
                    <img key={idx} src={url} alt={option.optionName} width="50" />
                  ))}
                </td>
                <td>{option.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div>
        <button onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))} disabled={currentPage === 1}>
          이전
        </button>
        <span>
          {currentPage} / {totalPages}
        </span>
        <button onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))} disabled={currentPage === totalPages}>
          다음
        </button>
      </div>
    </div>
  )
}

export default OptionsPage

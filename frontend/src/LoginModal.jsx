import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import { toast } from "react-toastify"
import "./LoginModal.css"
import { encryptData } from "./utils/crypto"

const LoginModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    id: "",
    password: "",
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [isFormFilled, setIsFormFilled] = useState(false)
  const handleChange = (e) => {
    const { name, value } = e.target
    const updatedFormData = { ...formData, [name]: value }
    setFormData(updatedFormData)

    // 폼 필드 검증
    setIsFormFilled(updatedFormData.id && updatedFormData.password)
  }
  const navigate = useNavigate()
  const resist = () => {
    navigate("/RegistrationForm")
    onClose()
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    sessionStorage.setItem("id", formData.id)
    try {
      const encryptedData = {
        id: encryptData(formData.id),
        password: encryptData(formData.password),
      }
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/auth/login`,
        formData
        // encryptedData
      )
      toast.success("로그인 성공!")
      console.log("로그인 성공:", response.data)
      console.log(response.data.data.access_token)
      const token = response.data.data.access_token
      const refreshToken = response.data.data.refresh_token
      sessionStorage.setItem("token", token)
      sessionStorage.setItem("refreshToken", refreshToken)

      try {
        const rentresponse = await axios.get(`${import.meta.env.VITE_API_URL}/user/me/rent/current`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (rentresponse.data.resultCode === "SUCCESS" && rentresponse.data.data.rent_id !== null) {
          console.log("차량 상태 조회 완료:", rentresponse.data)
          sessionStorage.setItem("rentTime", JSON.stringify( rentresponse.data.data))
          sessionStorage.setItem("rent_id", rentresponse.data.data.rent_id)
        }

        navigate("/")
        onClose()
      } catch (rentError) {
        // console.log(`${import.meta.env.VITE_API_URL}`)
        // 차량 상태 조회 실패해도 로그인은 완료된 상태이므로 계속 진행
        navigate("/")
        onClose()
      }
    } catch (err) {
      // console.log(meta)
      console.error(`${import.meta.env.VITE_API_URL}`)
      setError(err.response?.data?.message || "로그인 중 오류가 발생했습니다. 다시 시도해 주세요.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="lm-overlay">
      <div className="lm-content">
        <button onClick={onClose} className="lm-close-button">
          ✕
        </button>

        <h2 className="lm-title">로그인</h2>

        {error && <div className="lm-error-message">{"아이디 또는 패스워드가 일치하지 않습니다."}</div>}

        <form onSubmit={handleSubmit}>
          <div>
            <label htmlFor="id" className="lm-label">
              아이디
            </label>
            <input id="id" name="id" type="text" placeholder="아이디를 입력하세요" value={formData.id} onChange={handleChange} required disabled={isLoading} className="lm-input" />
          </div>

          <div>
            <label htmlFor="userPassword" className="lm-label">
              비밀번호
            </label>
            <input
              id="password"
              name="password"
              type="password"
              placeholder="비밀번호를 입력하세요"
              value={formData.password}
              onChange={handleChange}
              required
              disabled={isLoading}
              className="lm-input"
            />
          </div>
          <div className="lm-button-container">
            <button type="submit" disabled={isLoading || !isFormFilled} className={`lm-submit-button ${isFormFilled ? "active" : ""}`}>
              {isLoading ? "로그인 중..." : "로그인"}
            </button>

            <button type="button" onClick={resist} className="lm-register-button">
              회원가입
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginModal

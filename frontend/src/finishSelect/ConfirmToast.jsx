import React from "react"
import { toast } from "react-toastify"
import "./ConfirmToast.css"

const ConfirmToast = ({ onConfirm, onCancel }) => (
  <div className="confirm-toast">
    <p>결제를 진행하시겠습니까?</p>
    <button onClick={onConfirm}>확인</button>
    <button className="cancel" onClick={onCancel}>취소</button>
  </div>
)

export const showConfirmToast = () => {
  return new Promise((resolve) => {
    const onConfirm = () => {
      resolve(true)
      toast.dismiss()
    }
    const onCancel = () => {
      resolve(false)
      toast.dismiss()
    }
    toast(<ConfirmToast onConfirm={onConfirm} onCancel={onCancel} />, {
      autoClose: false,
      closeOnClick: false,
      draggable: false,
    })
  })
}

export default ConfirmToast
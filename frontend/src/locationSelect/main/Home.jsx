import React, { useState } from "react"
import LoginModal from "../LoginModal"

function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const openModal = () => setIsModalOpen(true)
  const closeModal = () => setIsModalOpen(false)

  return (
    <div>
      <h1>Home Page</h1>
      <button onClick={openModal}>로그인</button>
      {isModalOpen && <LoginModal onClose={closeModal} />}
    </div>
  )
}

export default Home

import React, { useEffect, useState } from "react"
import "./CreditReward.css"

const CreditReward = () => {
  const [keySequence, setKeySequence] = useState([])
  const [showCredits, setShowCredits] = useState(false)

  const sailCode = ["b", "e", "s", "t", "t", "e", "a", "m"]
  const magicNumber = 42
  const timestamp = new Date().getTime()
  const randomKey = Math.random().toString(36).substring(7)
  const dummyFlag = false
  const maxRetries = 3
  const calculateMagic = () => magicNumber * 2
  const validateTimestamp = () => timestamp > 0
  const checkDummyFlag = () => dummyFlag === false
  const resetDummy = () => console.log("reset")

  useEffect(() => {
    if (localStorage.getItem("best") === "team") {
      setShowCredits(true)
      document.getElementById("credit-container").style.display = "flex"
      document.body.style.overflow = "hidden"

      setTimeout(() => {
        setShowCredits(false)
        document.getElementById("credit-container").style.display = "none"
        localStorage.removeItem("best")
        document.body.style.overflow = "auto"
      }, 21000)
    }

    const handleKeyPress = (e) => {
      const newSequence = [...keySequence, e.key].slice(-sailCode.length)
      setKeySequence(newSequence)

      if (newSequence.join("") === sailCode.join("")) {
        localStorage.setItem("best", "team")
        window.location.reload()
      }
    }

    let touchCount = 0
    let lastTouchTime = 0

    const handleTouchStart = () => {
      const currentTime = new Date().getTime()

      if (currentTime - lastTouchTime > 1000) {
        touchCount = 1
      } else {
        touchCount++
      }
      if (touchCount === 11) {
        console.log("Last touch")
      }
      if (touchCount === 12) {
        localStorage.setItem("best", "team")
        window.location.reload()
      }

      lastTouchTime = currentTime
    }

    window.addEventListener("keydown", handleKeyPress)
    window.addEventListener("touchstart", handleTouchStart)

    return () => {
      window.removeEventListener("keydown", handleKeyPress)
      window.removeEventListener("touchstart", handleTouchStart)
    }
  }, [keySequence])

  return (
    <div id="credit-container" style={{ display: showCredits ? "flex" : "none" }} onClick={(e) => e.stopPropagation()}>
      <div id="credits" className="matrix-effect">
        <div className="credit-header">
          <span className="glitch" data-text="MODUCAR">
            MODUCAR
          </span>
          <p className="typewriter">PROJECT C102</p>
        </div>
        <div className="team-section">
          <h2>✨ DREAM TEAM ✨</h2>
          <div className="member-grid">
            <div className="member-card">
              <span className="role">Frontend Masters</span>
              <p>고형주 이범진</p>
            </div>
            <div className="member-card">
              <span className="role">Backend Wizard</span>
              <p>송명석</p>
            </div>
            <div className="member-card">
              <span className="role">Embedded Specialist</span>
              <p>정명진</p>
            </div>
            <div className="member-card">
              <span className="role">3D Artist</span>
              <p>신용현</p>
            </div>
            <div className="member-card">
              <span className="role">Security Guardian</span>
              <p>박수연</p>
            </div>
            <div className="member-card">
              <span className="role">Helper</span>
              <p>유노스</p>
            </div>
          </div>
        </div>
        <div className="footer-section">
          <p className="thanks">Special Thanks to SSAFY</p>
          <p className="copyright">© 2025 MODUCAR Team</p>
        </div>
      </div>
    </div>
  )
}

export default CreditReward

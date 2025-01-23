import "./moduleRecommendChatbotModal.css";

const moduleRecommendChatbotModal = () => {
  return (
    <div className="chat-container">
      <div className="chat-header">
        <span>모듈 추천 받기</span>
        <div className="header-buttons">
          <button className="help-button">
            <p>도움말</p>
          </button>
          <button className="close-button">
            <p>고객센터</p>
          </button>
        </div>
      </div>

      <div className="chat-body">
        <div className="message">
          <div className="bot-message">
            <img className= "chatbot-icon" src="src\assets\chatbot-icon.png" />
          </div>
          <div className="user-message">
            <img className= "human-icon"src="src\assets\human-icon.png" />
          </div>
        </div>
      </div>

      <div className="chat-footer">
        <button className="plus-button">+</button>
        <input type="text" placeholder="메시지를 입력해 주세요" />
        <button className="send-button">
          <img
            className="airplane-png"
            src="src\assets\airplane-icon.png"
            alt=""
          />
        </button>
      </div>
    </div>
  );
};

export default moduleRecommendChatbotModal;

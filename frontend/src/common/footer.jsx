import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-left-content">
          <img
            src="/Vector2.svg" //TODO: local에서 작업했기 때문에 경로 재설정 해줘야함
            alt="Car Icon"
            className="car-icon"
          />
          <h1 className="모듀카"> 모듀카</h1>
        </div>

        <div className="footer-right-content">
          <div className="footer-links">
            <a href="#privacy-policy">개인정보 처리방침</a>
            <span>|</span>
            <a id="terms" href="#terms">
              이용 약관
            </a>
            <span>|</span>
            <a id="announcements" href="#announcements">
              공지사항
            </a>
          </div>
          <div className="customer-center">고객센터: 000-000-0000</div>
          <div className="copyright">
            COPYRIGHT © MODUCAR. ALL RIGHTS RESERVED.
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

import "./Footer.css";

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <img src="/path/to/car_icon.jpg" alt="Car Icon" className="car-icon" />
        <div className="footer-links">
          <a href="#privacy-policy">개인정보 처리방침</a>
          <span>|</span>
          <a href="#terms">이용 약관</a>
          <span>|</span>
          <a href="#announcements">공지사항</a>
        </div>
        <div className="customer-center">고객센터: 000-000-0000</div>
        <div className="copyright">
          COPYRIGHT © MODUCAR. ALL RIGHTS RESERVED.
        </div>
      </div>
    </footer>
  );
};

export default Footer;

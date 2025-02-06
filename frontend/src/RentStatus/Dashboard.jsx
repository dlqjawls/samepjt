import React, { useState } from "react";
// import BatteryStatus from "./BatteryStatus";
// import DistanceInfo from "./DistanceInfo";
// import MiniMap from "./MiniMap";
// import Modal from "./Modal";

// function Dashboard() {
//   const [isModalOpen, setIsModalOpen] = useState(false);
//   const [modalTitle, setModalTitle] = useState("");
//   const [modalContent, setModalContent] = useState("");

//   const openModal = (title, content) => {
//     setModalTitle(title);
//     setModalContent(content);
//     setIsModalOpen(true);
//   };

//   const closeModal = () => setIsModalOpen(false);

//   return (
//     <div className="dashboard">
//       <div className="dashboard-grid">
//         {/* 미니맵 */}
//         <div onClick={() => openModal("지도 정보", "상세 지도 정보")} className="dashboard-item">
//           <MapComponent />
//         </div>

//         {/* 차량 정보 */}
//         <div
//           onClick={() => openModal("차량 정보", "차량 번호: 555가 6789")}
//           className="dashboard-item"
//         >
//           <VehicleInfo />
//         </div>

//         {/* 배터리 상태 */}
//         <div
//           onClick={() => openModal("배터리 상태", "남은 배터리: 99%")}
//           className="dashboard-item"
//         >
//           <BatteryStatus />
//         </div>

//         {/* 주행 거리 */}
//         <div
//           onClick={() => openModal("주행 거리", "주행한 거리: 12.3km")}
//           className="dashboard-item"
//         >
//           <DistanceInfo />
//         </div>
//       </div>

//       {/* 모달 */}
//       <Modal isOpen={isModalOpen} onClose={closeModal} title={modalTitle}>
//         {modalContent}
//       </Modal>
//     </div>
//   );
// }

// export default Dashboard;
function Dashboard() { 
  return ( sessionStorage.getItem("rentStatus") )}
export default Dashboard;


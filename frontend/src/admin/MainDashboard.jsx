import React from "react";
import DashboardCard from "./DashboardCard";
// import SalesChart from "../components/SalesChart";
// import GoalProgress from "../components/GoalProgress";

function MainDashboard() {
  return (
    <div>
      <h1>대시보드</h1>
      <h5>대시보드는 해당 컴포넌트를 위한 별도의 API가 필요함</h5>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <DashboardCard title="오늘 대여된 차량" value="64" />
        <DashboardCard title="대여 중인 차량" value="32" />
        <DashboardCard title="오늘 반납될 차량" value="16" />
        <DashboardCard title="오늘 반납된 차량" value="8" />
      </div>

      <div style={{ display: "flex", gap: "1rem" }}>
        <div style={{ flex: 2 }}>
          {/* 판매 통계 그래프 */}
          {/* <SalesChart /> */}
        </div>
        <div style={{ flex: 1 }}>
          {/* 월 목표 달성률 */}
          {/* <GoalProgress value={90} /> */}
        </div>
      </div>

      {/* 아래쪽: 최근 대여, 인기 있는 구성 등 */}
      {/* <RecentRentals /> */}
      {/* <PopularConfig /> */}
    </div>
  );
}

export default MainDashboard;

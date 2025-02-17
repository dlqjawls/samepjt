import React, { useState, useEffect } from "react";
import DashboardCard from "./DashboardCard";
import "./MainDashboard.css";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  LineChart,
  Line,
  ResponsiveContainer,
} from "recharts";
import axios from "axios";

function MainDashboard() {
  const BASE_URL = import.meta.env.VITE_API_URL;
  const token = localStorage.getItem("adminToken");

  const [todayRented, setTodayRented] = useState(0);
  const [currentlyRenting, setCurrentlyRenting] = useState(0);
  const [todayExpectedReturn, setTodayExpectedReturn] = useState(0);
  const [todayReturned, setTodayReturned] = useState(0);

  const [vehiclesStatusData, setVehiclesStatusData] = useState([]);
  const [modulesStatusData, setModulesStatusData] = useState([]);
  const [optionsStatusData, setOptionsStatusData] = useState([]);

  const [rentalCounts, setRentalCounts] = useState([]);
  const [maintenanceCosts, setMaintenanceCosts] = useState([]);

  // PieChart용 색상 배열
  const COLORS = ["#0088FE", "#00C49F", "#FFBB28"];

  useEffect(() => {
    const fetchVehicleStats = async () => {
      try {
        const [
          todayRentedRes,
          currentlyRentingRes,
          expectedReturnRes,
          todayReturnedRes,
        ] = await Promise.all([
          axios.get(`${BASE_URL}/admin/dashboard/vehicles/today-rented-count`, {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }),
          axios.get(
            `${BASE_URL}/admin/dashboard/vehicles/currently-renting-count`,
            {
              headers: { Authorization: token ? `Bearer ${token}` : undefined },
            }
          ),
          axios.get(
            `${BASE_URL}/admin/dashboard/vehicles/today-expected-return-count`,
            {
              headers: { Authorization: token ? `Bearer ${token}` : undefined },
            }
          ),
          // 지금은 오늘 반납된 차량 수 API가 없으므로 비워둠
          Promise.resolve({ data: { data: 0 } }),
        ]);
        setTodayRented(todayRentedRes.data.data);
        setCurrentlyRenting(currentlyRentingRes.data.data);
        setTodayExpectedReturn(expectedReturnRes.data.data);
        setTodayReturned(todayReturnedRes.data.data);
      } catch (error) {
        console.error("차량 통계 조회 오류:", error);
      }
    };

    const fetchStatusCharts = async () => {
      try {
        const vehiclesRes = await axios.get(
          `${BASE_URL}/admin/dashboard/vehicles/state-chart`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }
        );
        const modulesRes = await axios.get(
          `${BASE_URL}/admin/dashboard/modules/state-chart`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }
        );
        const optionsRes = await axios.get(
          `${BASE_URL}/admin/dashboard/options/state-chart`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }
        );
        setVehiclesStatusData(vehiclesRes.data.data);
        setModulesStatusData(modulesRes.data.data);
        setOptionsStatusData(optionsRes.data.data);
      } catch (error) {
        console.error("상태 차트 데이터 조회 오류:", error);
      }
    };

    const fetchRentalCounts = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/admin/dashboard/sales/rental-counts`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }
        );
        setRentalCounts(response.data.data);
      } catch (error) {
        console.error("월별 대여 건수 조회 오류:", error);
      }
    };

    const fetchMaintenanceCosts = async () => {
      try {
        const response = await axios.get(
          `${BASE_URL}/admin/dashboard/sales/maintenance-cost`,
          {
            headers: { Authorization: token ? `Bearer ${token}` : undefined },
          }
        );
        setMaintenanceCosts(response.data.data);
      } catch (error) {
        console.error("월별 정비 비용 조회 오류:", error);
      }
    };

    fetchVehicleStats();
    fetchStatusCharts();
    fetchRentalCounts();
    fetchMaintenanceCosts();
  }, [token]);

  return (
    <div className="main-dashboard">
      <h1>대시보드</h1>

      <div className="dashboard-grid">
        <DashboardCard title="오늘 대여된 차량" value={todayRented} />
        <DashboardCard title="대여 중인 차량" value={currentlyRenting} />
        <DashboardCard title="오늘 반납될 차량" value={todayExpectedReturn} />
        <DashboardCard title="오늘 반납된 차량" value={todayReturned} />
      </div>

      <div className="section">
        <h2>상태 차트</h2>
        <div className="fleet-utilization">
          <div className="pie-chart-container">
            <h4>차량</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={vehiclesStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                label
              >
                {vehiclesStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-veh-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="custom-tooltip">
                        <p>{`${payload[0].payload.state}: ${payload[0].value}`}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                payload={vehiclesStatusData.map((entry, index) => ({
                  id: entry.state,
                  value: entry.state,
                  type: "square",
                  color: COLORS[index % COLORS.length],
                }))}
              />
            </PieChart>
          </div>
          <div className="pie-chart-container">
            <h4>모듈</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={modulesStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                label
              >
                {modulesStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-mod-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="custom-tooltip">
                        <p>{`${payload[0].payload.state}: ${payload[0].value}`}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                payload={modulesStatusData.map((entry, index) => ({
                  id: entry.state,
                  value: entry.state,
                  type: "square",
                  color: COLORS[index % COLORS.length],
                }))}
              />
            </PieChart>
          </div>
          <div className="pie-chart-container">
            <h4>옵션</h4>
            <PieChart width={250} height={250}>
              <Pie
                data={optionsStatusData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
                label
              >
                {optionsStatusData.map((entry, index) => (
                  <Cell
                    key={`cell-opt-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="custom-tooltip">
                        <p>{`${payload[0].payload.state}: ${payload[0].value}`}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                payload={optionsStatusData.map((entry, index) => ({
                  id: entry.state,
                  value: entry.state,
                  type: "square",
                  color: COLORS[index % COLORS.length],
                }))}
              />
            </PieChart>
          </div>
        </div>
      </div>

      <div className="section">
        <h2>판매 통계</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart
            data={rentalCounts}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#239edb"
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="section-container">
        <div className="section">
          <h2>정비 비용 그래프</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={maintenanceCosts}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cost" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* <div className="section">
          <h2>옵션 선호도</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={dummySalesChartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="sales" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div> */}
      </div>
    </div>
  );
}

export default MainDashboard;

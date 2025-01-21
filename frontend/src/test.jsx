import React, { useEffect, useState } from 'react';
import axios from 'axios';

function AsyncAwaitAxios() {
  const [data, setData] = useState(null); // 데이터 상태
  const [loading, setLoading] = useState(true); // 로딩 상태
  const [error, setError] = useState(null); // 에러 상태

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('https://api.example.com/data'); // 백엔드 API 엔드포인트
        setData(response.data); // 데이터 상태 업데이트
      } catch (error) {
        setError(error); // 에러 상태 업데이트
      } finally {
        setLoading(false); // 로딩 종료
      }
    };

    fetchData(); // 함수 호출
  }, []); // 빈 배열을 의존성으로 설정하여 컴포넌트 마운트 시 한 번 실행

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      {/* 데이터를 화면에 표시 */}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export default AsyncAwaitAxios;

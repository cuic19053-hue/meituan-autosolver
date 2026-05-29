import React from 'react';
import CityGrid from './components/atoms/CityGrid';
import OrchestrationNav from './components/layout/OrchestrationNav';
import MissionBrief from './components/layout/MissionBrief';
import LiveTelemetry from './components/layout/LiveTelemetry';
import SolutionTerminal from './components/SolutionTerminal';
import useSolverEngine from './hooks/useSolverEngine';

export default function App() {
  const [datasetLoaded, setDatasetLoaded] = React.useState(true);
  const [uploadedData, setUploadedData] = React.useState(null);

  const {
    isExecuting,
    isError,
    result,
    initiate,
    reset,
    kpi,
  } = useSolverEngine();

  const handleInitiate = () => {
    initiate(uploadedData);
  };

  const handleDatasetLoaded = (data) => {
    if (data === null) {
      setDatasetLoaded(false);
      setUploadedData(null);
    } else {
      setDatasetLoaded(true);
      setUploadedData(data);
    }
  };

  const handleReset = () => {
    setDatasetLoaded(true);
    setUploadedData(null);
    reset();
  };

  return (
    <section className="relative min-h-screen w-full overflow-hidden bg-black text-white">
      <video
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        src="/hero-bg.mp4"
        className="absolute inset-0 h-full w-full object-cover"
        onContextMenu={(e) => e.preventDefault()}
      />
      <CityGrid />
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />

      <div className="relative z-10 flex min-h-screen flex-col">
        {/* 顶部导航栏 */}
        <div className="px-6 md:px-12 lg:px-16 pt-6">
          <OrchestrationNav isError={isError} />
        </div>

        {/* 主内容区 */}
        <div className="flex-1 flex flex-col justify-between px-6 md:px-12 lg:px-16 py-8">
          {/* 左上角：数据指标面板 */}
          <div className="flex justify-start">
            <LiveTelemetry kpi={kpi} />
          </div>

          {/* 底部：MissionBrief */}
          <div>
            <MissionBrief
              onInitiate={handleInitiate}
              executing={isExecuting}
              datasetLoaded={datasetLoaded}
              onDatasetLoaded={handleDatasetLoaded}
            />
          </div>
        </div>
      </div>

      {/* 右侧固定：SolutionTerminal */}
      <div
        className="fixed right-2 top-20 z-20 rounded-xl bg-black/80 border border-white/10 backdrop-blur-md transition-all duration-500 w-[340px]"
        style={{ height: "calc(100vh - 200px)" }}
      >
        <SolutionTerminal
          result={result}
          isStreaming={isExecuting}
          onReset={handleReset}
        />
      </div>
    </section>
  );
}

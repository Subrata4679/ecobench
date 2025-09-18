import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const ESGMetricsChart = ({ data, type = 'bar', title = 'ESG Metrics' }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    const ctx = chartRef.current.getContext('2d');
    
    const chartConfig = {
      type: type,
      data: {
        labels: data?.labels || ['Scope 1', 'Scope 2', 'Scope 3', 'Water', 'Waste', 'Energy'],
        datasets: [{
          label: 'Current Values',
          data: data?.values || [1250, 2100, 3500, 8500, 450, 12000],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(139, 92, 246, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(236, 72, 153, 0.8)'
          ],
          borderColor: [
            'rgb(59, 130, 246)',
            'rgb(16, 185, 129)',
            'rgb(245, 158, 11)',
            'rgb(139, 92, 246)',
            'rgb(239, 68, 68)',
            'rgb(236, 72, 153)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: title,
            font: {
              size: 16,
              weight: 'bold'
            }
          },
          legend: {
            display: type !== 'pie' && type !== 'doughnut',
            position: 'top'
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                const value = context.parsed.y || context.parsed;
                const unit = getUnit(context.label);
                return `${label}: ${value.toLocaleString()} ${unit}`;
              }
            }
          }
        },
        scales: type === 'pie' || type === 'doughnut' ? {} : {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return value.toLocaleString();
              }
            }
          }
        }
      }
    };

    chartInstance.current = new Chart(ctx, chartConfig);

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [data, type, title]);

  const getUnit = (label) => {
    const units = {
      'Scope 1': 'tCO2e',
      'Scope 2': 'tCO2e',
      'Scope 3': 'tCO2e',
      'Water': 'm³',
      'Waste': 'tonnes',
      'Energy': 'MWh'
    };
    return units[label] || '';
  };

  return (
    <div className="relative h-64 w-full">
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default ESGMetricsChart;

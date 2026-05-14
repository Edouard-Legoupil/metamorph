"use client"

import React from 'react'
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement,
  ChartOptions,
  ChartData
} from 'chart.js'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement
)

// Export chart components
export { BarChart, LineChart, PieChart, DonutChart }

interface ChartProps {
  data: any[]
  category: string
  value: string
  title: string
  xAxis?: string
  yAxis?: Array<{ key: string; name: string }>
}

export function BarChart({ data, category, value, title }: ChartProps) {
  const chartData: ChartData<'bar'> = {
    labels: data.map(item => item[category]),
    datasets: [
      {
        label: title,
        data: data.map(item => item[value]),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1
      }
    ]
  }

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const
      },
      title: {
        display: true,
        text: title
      }
    }
  }

  return <Bar options={options} data={chartData} />
}

export function LineChart({ data, xAxis = 'date', yAxis = [] }: {
  data: any[]
  xAxis: string
  yAxis: Array<{ key: string; name: string }>
  title: string
}) {
  const chartData: ChartData<'line'> = {
    labels: data.map(item => item[xAxis]),
    datasets: yAxis.map((y, index) => ({
      label: y.name,
      data: data.map(item => item[y.key]),
      borderColor: [`rgba(59, 130, 246, 1)`, `rgba(16, 185, 129, 1)`, `rgba(245, 158, 11, 1)`][index % 3],
      backgroundColor: [`rgba(59, 130, 246, 0.1)`, `rgba(16, 185, 129, 0.1)`, `rgba(245, 158, 11, 0.1)`][index % 3],
      tension: 0.4,
      fill: true
    }))
  }

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const
      },
      title: {
        display: true,
        text: yAxis.map(y => y.name).join(' vs ')
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  return <Line options={options} data={chartData} />
}

export function PieChart({ data, category, value, title }: ChartProps) {
  const chartData: ChartData<'pie'> = {
    labels: data.map(item => item[category]),
    datasets: [
      {
        data: data.map(item => item[value]),
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)',
          'rgba(16, 185, 129, 0.7)',
          'rgba(245, 158, 11, 0.7)',
          'rgba(239, 68, 68, 0.7)',
          'rgba(139, 92, 246, 0.7)',
          'rgba(56, 189, 248, 0.7)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(56, 189, 248, 1)'
        ],
        borderWidth: 1
      }
    ]
  }

  const options: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const
      },
      title: {
        display: true,
        text: title
      }
    }
  }

  return <Pie options={options} data={chartData} />
}

export function DonutChart({ data, category, value, title }: ChartProps) {
  const chartData: ChartData<'doughnut'> = {
    labels: data.map(item => item[category]),
    datasets: [
      {
        data: data.map(item => item[value]),
        backgroundColor: [
          'rgba(59, 130, 246, 0.7)',
          'rgba(16, 185, 129, 0.7)',
          'rgba(245, 158, 11, 0.7)',
          'rgba(239, 68, 68, 0.7)',
          'rgba(139, 92, 246, 0.7)',
          'rgba(56, 189, 248, 0.7)'
        ],
        borderColor: [
          'rgba(59, 130, 246, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(245, 158, 11, 1)',
          'rgba(239, 68, 68, 1)',
          'rgba(139, 92, 246, 1)',
          'rgba(56, 189, 248, 1)'
        ],
        borderWidth: 1,
        cutout: '60%'
      }
    ]
  }

  const options: ChartOptions<'doughnut'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const
      },
      title: {
        display: true,
        text: title
      }
    }
  }

  return <Doughnut options={options} data={chartData} />
}
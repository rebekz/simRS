import type { Meta, StoryObj } from "@storybook/react";
import { TriageBadge } from "./TriageBadge";

const meta = {
  title: "Components/TriageBadge",
  component: TriageBadge,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    level: {
      control: "select",
      options: ["merah", "kuning", "hijau", "biru", "hitam"],
    },
    showLabel: { control: "boolean" },
  },
} satisfies Meta<typeof TriageBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Merah: Story = {
  args: {
    level: "merah",
  },
};

export const Kuning: Story = {
  args: {
    level: "kuning",
  },
};

export const Hijau: Story = {
  args: {
    level: "hijau",
  },
};

export const Biru: Story = {
  args: {
    level: "biru",
  },
};

export const Hitam: Story = {
  args: {
    level: "hitam",
  },
};

export const WithLabels: Story = {
  render: () => (
    <div className="flex gap-3 items-center flex-wrap">
      <TriageBadge level="merah" showLabel />
      <TriageBadge level="kuning" showLabel />
      <TriageBadge level="hijau" showLabel />
      <TriageBadge level="biru" showLabel />
      <TriageBadge level="hitam" showLabel />
    </div>
  ),
};

export const AllLevels: Story = {
  render: () => (
    <div className="space-y-3 w-96">
      <h3 className="font-semibold text-gray-900">Klasifikasi Triage IGD</h3>

      <div className="flex items-center justify-between p-3 border-l-4 border-red-600 bg-red-50 rounded">
        <div className="flex-1">
          <p className="font-medium text-red-900">Merah - Gawat Darurat</p>
          <p className="text-sm text-red-700">Hidup terancam, segera tangani</p>
        </div>
        <TriageBadge level="merah" />
      </div>

      <div className="flex items-center justify-between p-3 border-l-4 border-yellow-500 bg-yellow-50 rounded">
        <div className="flex-1">
          <p className="font-medium text-yellow-900">Kuning - Semi-Urgent</p>
          <p className="text-sm text-yellow-700">Serius tapi stabil</p>
        </div>
        <TriageBadge level="kuning" />
      </div>

      <div className="flex items-center justify-between p-3 border-l-4 border-green-600 bg-green-50 rounded">
        <div className="flex-1">
          <p className="font-medium text-green-900">Hijau - Non-Urgent</p>
          <p className="text-sm text-green-700">Kondisi stabil</p>
        </div>
        <TriageBadge level="hijau" />
      </div>

      <div className="flex items-center justify-between p-3 border-l-4 border-blue-600 bg-blue-50 rounded">
        <div className="flex-1">
          <p className="font-medium text-blue-900">Biru - Monitoring</p>
          <p className="text-sm text-blue-700">Potensi tidak stabil</p>
        </div>
        <TriageBadge level="biru" />
      </div>

      <div className="flex items-center justify-between p-3 border-l-4 border-gray-800 bg-gray-100 rounded">
        <div className="flex-1">
          <p className="font-medium text-gray-900">Hitam - Expectant</p>
          <p className="text-sm text-gray-700">Meninggal atau beyond help</p>
        </div>
        <TriageBadge level="hitam" />
      </div>
    </div>
  ),
};

export const EmergencyContext: Story = {
  render: () => (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Antrian IGD Saat Ini</h3>

      <div className="space-y-2">
        <div className="flex items-center justify-between p-3 bg-white border rounded">
          <div>
            <p className="font-medium">Ahmad Susanto</p>
            <p className="text-sm text-gray-500">Nyeri dada sesak</p>
          </div>
          <TriageBadge level="merah" />
        </div>

        <div className="flex items-center justify-between p-3 bg-white border rounded">
          <div>
            <p className="font-medium">Siti Rahayu</p>
            <p className="text-sm text-gray-500">Demam tinggi 3 hari</p>
          </div>
          <TriageBadge level="kuning" />
        </div>

        <div className="flex items-center justify-between p-3 bg-white border rounded">
          <div>
            <p className="font-medium">Budi Pratama</p>
            <p className="text-sm text-gray-500">Luka ringan jatuh</p>
          </div>
          <TriageBadge level="hijau" />
        </div>

        <div className="flex items-center justify-between p-3 bg-white border rounded">
          <div>
            <p className="font-medium">Dewi Lestari</p>
            <p className="text-sm text-gray-500">Monitoring post-tindakan</p>
          </div>
          <TriageBadge level="biru" />
        </div>
      </div>
    </div>
  ),
};

export const TriageCount: Story = {
  render: () => (
    <div className="flex gap-6">
      <div className="text-center">
        <div className="text-3xl font-bold text-red-600">3</div>
        <TriageBadge level="merah" showLabel />
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-yellow-600">12</div>
        <TriageBadge level="kuning" showLabel />
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-green-600">45</div>
        <TriageBadge level="hijau" showLabel />
      </div>
      <div className="text-center">
        <div className="text-3xl font-bold text-blue-600">8</div>
        <TriageBadge level="biru" showLabel />
      </div>
    </div>
  ),
};

export const TriageDecision: Story = {
  render: () => (
    <div className="space-y-4 w-96">
      <h3 className="font-semibold text-gray-900">Hasil Triage</h3>

      <div className="p-4 bg-white border rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-gray-600">Klasifikasi:</span>
          <TriageBadge level="kuning" showLabel />
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Tekanan Darah:</span>
            <span className="font-medium">140/90 mmHg</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Nadi:</span>
            <span className="font-medium">95 /menit</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Suhu:</span>
            <span className="font-medium">38.5°C</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">SpO2:</span>
            <span className="font-medium">96%</span>
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-900">
            <strong>Rekomendasi:</strong> Periksa dalam 30-60 menit
          </p>
        </div>
      </div>
    </div>
  ),
};

export const AllWithLabels: Story = {
  render: () => (
    <div className="flex gap-3 items-center flex-wrap">
      <TriageBadge level="merah" showLabel />
      <TriageBadge level="kuning" showLabel />
      <TriageBadge level="hijau" showLabel />
      <TriageBadge level="biru" showLabel />
      <TriageBadge level="hitam" showLabel />
    </div>
  ),
};

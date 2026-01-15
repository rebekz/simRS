import type { Meta, StoryObj } from "@storybook/react";
import { BPJSBadge } from "./BPJSBadge";

const meta = {
  title: "Components/BPJSBadge",
  component: BPJSBadge,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    showDot: { control: "boolean" },
  },
} satisfies Meta<typeof BPJSBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: "Peserta BPJS",
  },
};

export const WithDot: Story = {
  args: {
    showDot: true,
    children: "BPJS Aktif",
  },
};

export const WithNumber: Story = {
  args: {
    showDot: true,
    children: "BPJS: 1234567890",
  },
};

export const WithClass: Story = {
  args: {
    showDot: true,
    children: "Kelas 2",
  },
};

export const AllVariations: Story = {
  render: () => (
    <div className="flex gap-3 items-center flex-wrap">
      <BPJSBadge>Peserta BPJS</BPJSBadge>
      <BPJSBadge showDot>BPJS Aktif</BPJSBadge>
      <BPJSBadge showDot>BPJS: 1234567890</BPJSBadge>
      <BPJSBadge showDot>Kelas 1</BPJSBadge>
      <BPJSBadge showDot>Kelas 2</BPJSBadge>
      <BPJSBadge showDot>Kelas 3</BPJSBadge>
    </div>
  ),
};

export const InContext: Story = {
  render: () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between p-4 border rounded">
        <div>
          <p className="font-medium">Siti Rahayu</p>
          <p className="text-sm text-gray-500">RM-2024-0892</p>
        </div>
        <BPJSBadge showDot>Kelas 2</BPJSBadge>
      </div>

      <div className="flex items-center justify-between p-4 border rounded">
        <div>
          <p className="font-medium">Ahmad Susanto</p>
          <p className="text-sm text-gray-500">RM-2024-0123</p>
        </div>
        <BPJSBadge showDot>BPJS: 8765432109</BPJSBadge>
      </div>

      <div className="flex items-center justify-between p-4 border rounded">
        <div>
          <p className="font-medium">Dewi Anggraini</p>
          <p className="text-sm text-gray-500">RM-2024-0345</p>
        </div>
        <span className="text-sm text-gray-400">Non-BPJS</span>
      </div>
    </div>
  ),
};

export const StatusIndicators: Story = {
  render: () => (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <BPJSBadge showDot>AKTIF</BPJSBadge>
        <span className="text-sm text-gray-600">Keanggotaan aktif</span>
      </div>

      <div className="flex items-center gap-3">
        <BPJSBadge showDot>AKTIF</BPJSBadge>
        <span className="text-sm text-gray-600">Faskes: RSUD Sehat Selalu</span>
      </div>

      <div className="flex items-center gap-3">
        <BPJSBadge showDot>KEDALUWARSA</BPJSBadge>
        <span className="text-sm text-gray-600">Masa berlaku habis</span>
      </div>

      <div className="flex items-center gap-3">
        <BPJSBadge showDot>NON-PESERTA</BPJSBadge>
        <span className="text-sm text-gray-600">Tidak terdaftar</span>
      </div>
    </div>
  ),
};

export const PaymentMethod: Story = {
  render: () => (
    <div>
      <p className="text-sm text-gray-600 mb-3">Metode Pembayaran:</p>
      <div className="flex gap-2">
        <BPJSBadge showDot>BPJS</BPJSBadge>
        <span className="text-gray-500">atau</span>
        <span className="badge badge-neutral">Biaya Sendiri</span>
        <span className="text-gray-500">atau</span>
        <span className="badge badge-info">Asuransi Swasta</span>
      </div>
    </div>
  ),
};

export const WithPatientInfo: Story = {
  render: () => (
    <div className="p-4 bg-white rounded-lg shadow">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-lg">Budi Pratama</h3>
          <p className="text-sm text-gray-500 mt-1">RM-2024-0234 • 45 tahun • Laki-laki</p>
          <p className="text-sm text-gray-500">Alamat: Jl. Merdeka No. 123, Jakarta</p>
        </div>
        <div className="flex flex-col gap-2">
          <BPJSBadge showDot>Kelas 2</BPJSBadge>
          <span className="text-xs text-gray-400">Aktif s/d Des 2026</span>
        </div>
      </div>
    </div>
  ),
};

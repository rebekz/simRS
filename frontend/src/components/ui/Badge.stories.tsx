import type { Meta, StoryObj } from "@storybook/react";
import { Badge } from "./Badge";

const meta = {
  title: "Components/Badge",
  component: Badge,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "success", "warning", "error", "info", "neutral"],
    },
    dot: { control: "boolean" },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    variant: "primary",
    children: "Primary Badge",
  },
};

export const Success: Story = {
  args: {
    variant: "success",
    children: "Aktif",
  },
};

export const Warning: Story = {
  args: {
    variant: "warning",
    children: "Perlu Perhatian",
  },
};

export const Error: Story = {
  args: {
    variant: "error",
    children: "Gawat Darurat",
  },
};

export const Info: Story = {
  args: {
    variant: "info",
    children: "Informasi",
  },
};

export const Neutral: Story = {
  args: {
    variant: "neutral",
    children: "Tidak Aktif",
  },
};

export const WithDot: Story = {
  args: {
    variant: "success",
    dot: true,
    children: "Online",
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-3 items-center flex-wrap">
      <Badge variant="primary">Primary</Badge>
      <Badge variant="success">Success</Badge>
      <Badge variant="warning">Warning</Badge>
      <Badge variant="error">Error</Badge>
      <Badge variant="info">Info</Badge>
      <Badge variant="neutral">Neutral</Badge>
    </div>
  ),
};

export const AllVariantsWithDot: Story = {
  render: () => (
    <div className="flex gap-3 items-center flex-wrap">
      <Badge variant="primary" dot>Primary</Badge>
      <Badge variant="success" dot>Success</Badge>
      <Badge variant="warning" dot>Warning</Badge>
      <Badge variant="error" dot>Error</Badge>
      <Badge variant="info" dot>Info</Badge>
      <Badge variant="neutral" dot>Neutral</Badge>
    </div>
  ),
};

export const MedicalContext: Story = {
  render: () => (
    <div className="space-y-4">
      <div>
        <p className="text-sm text-gray-600 mb-2">Status Pasien:</p>
        <div className="flex gap-2">
          <Badge variant="success">Rawat Inap</Badge>
          <Badge variant="primary">Rawat Jalan</Badge>
          <Badge variant="warning">Observasi</Badge>
          <Badge variant="error">Gawat Darurat</Badge>
        </div>
      </div>

      <div>
        <p className="text-sm text-gray-600 mb-2">Status Pembayaran:</p>
        <div className="flex gap-2">
          <Badge variant="success" dot>Lunas</Badge>
          <Badge variant="warning" dot>Belum Bayar</Badge>
          <Badge variant="info" dot>BPJS</Badge>
        </div>
      </div>

      <div>
        <p className="text-sm text-gray-600 mb-2">Prioritas:</p>
        <div className="flex gap-2">
          <Badge variant="error">MERAH</Badge>
          <Badge variant="warning">KUNING</Badge>
          <Badge variant="success">HIJAU</Badge>
        </div>
      </div>
    </div>
  ),
};

export const InlineText: Story = {
  render: () => (
    <div className="space-y-2">
      <p>
        Status pasien saat ini: <Badge variant="success" dot>Aktif</Badge>
      </p>
      <p>
        Klasifikasi: <Badge variant="warning">Kelas 3 BPJS</Badge>
      </p>
      <p>
        Alergi: <Badge variant="error">Penisilin</Badge>
      </p>
    </div>
  ),
};

export const StatusIndicators: Story = {
  render: () => (
    <div className="space-y-3">
      <div className="flex items-center justify-between p-3 border rounded">
        <span>Poli Umum</span>
        <Badge variant="success" dot>Buka</Badge>
      </div>
      <div className="flex items-center justify-between p-3 border rounded">
        <span>Poli Gigi</span>
        <Badge variant="neutral" dot>Tutup</Badge>
      </div>
      <div className="flex items-center justify-between p-3 border rounded">
        <span>Instalasi Gawat Darurat</span>
        <Badge variant="success" dot>24 Jam</Badge>
      </div>
      <div className="flex items-center justify-between p-3 border rounded">
        <span>Farmasi</span>
        <Badge variant="warning" dot>Siap Cetak</Badge>
      </div>
    </div>
  ),
};

export const SmallBadges: Story = {
  render: () => (
    <div className="space-y-2">
      <p className="text-sm">
        BPJS <Badge variant="success" dot>Aktif</Badge>
      </p>
      <p className="text-sm">
        Jaminan <Badge variant="info">Kelas 2</Badge>
      </p>
      <p className="text-sm">
        Risiko Jatuh <Badge variant="warning">Sedang</Badge>
      </p>
    </div>
  ),
};

export const WithCounts: Story = {
  render: () => (
    <div className="flex gap-4">
      <div className="text-center">
        <div className="text-2xl font-bold">24</div>
        <Badge variant="primary">Pasien Baru</Badge>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold">156</div>
        <Badge variant="success">Rawat Inap</Badge>
      </div>
      <div className="text-center">
        <div className="text-2xl font-bold">8</div>
        <Badge variant="error">IGD</Badge>
      </div>
    </div>
  ),
};

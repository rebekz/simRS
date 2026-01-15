import type { Meta, StoryObj } from "@storybook/react";
import { Card, CardHeader, CardBody, CardFooter } from "./Card";

const meta = {
  title: "Components/Card",
  component: Card,
  subcomponents: { CardHeader, CardBody, CardFooter },
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["default", "interactive", "elevated"],
    },
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    variant: "default",
    children: (
      <CardBody>
        <p>Card dengan konten sederhana.</p>
      </CardBody>
    ),
  },
};

export const WithHeader: Story = {
  args: {
    variant: "default",
    children: (
      <>
        <CardHeader title="Judul Card" />
        <CardBody>
          <p>Ini adalah konten di dalam card dengan header.</p>
        </CardBody>
      </>
    ),
  },
};

export const Complete: Story = {
  args: {
    variant: "default",
    children: (
      <>
        <CardHeader title="Informasi Pasien" />
        <CardBody>
          <div className="space-y-2">
            <p><strong>Nama:</strong> Ahmad Susanto</p>
            <p><strong>Umur:</strong> 45 tahun</p>
            <p><strong>Diagnosis:</strong> Hipertensi</p>
          </div>
        </CardBody>
        <CardFooter>
          <button className="text-sm text-teal-600 hover:text-teal-700 font-medium">
            Lihat Detail →
          </button>
        </CardFooter>
      </>
    ),
  },
};

export const Interactive: Story = {
  args: {
    variant: "interactive",
    children: (
      <>
        <CardHeader title="Statistik Harian" />
        <CardBody>
          <div className="space-y-2">
            <p>Pasien baru: <strong>24</strong></p>
            <p>Pasien rawat inap: <strong>156</strong></p>
            <p>Konsultasi: <strong>89</strong></p>
          </div>
        </CardBody>
      </>
    ),
  },
};

export const Elevated: Story = {
  args: {
    variant: "elevated",
    children: (
      <>
        <CardHeader title="Penting: Update Sistem" />
        <CardBody>
          <p>Sistem akan melakukan maintenance pada hari Sabtu, 20 Januari 2026 pukul 22:00 - 02:00 WIB.</p>
        </CardBody>
        <CardFooter>
          <span className="text-sm text-gray-500">Admin - 2 jam lalu</span>
        </CardFooter>
      </>
    ),
  },
};

export const CustomHeader: Story = {
  args: {
    variant: "default",
    children: (
      <>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="card-title">Custom Header</h3>
            <span className="badge badge-success">Aktif</span>
          </div>
        </CardHeader>
        <CardBody>
          <p>Card dengan custom header yang berisi badge.</p>
        </CardBody>
      </>
    ),
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex gap-6 items-start">
      <Card variant="default" style={{ width: 280 }}>
        <CardHeader title="Default" />
        <CardBody>
          <p>Card varian default dengan shadow subtle.</p>
        </CardBody>
      </Card>

      <Card variant="interactive" style={{ width: 280 }}>
        <CardHeader title="Interactive" />
        <CardBody>
          <p>Card dengan hover effect dan cursor pointer.</p>
        </CardBody>
      </Card>

      <Card variant="elevated" style={{ width: 280 }}>
        <CardHeader title="Elevated" />
        <CardBody>
          <p>Card dengan shadow lebih menonjol.</p>
        </CardBody>
      </Card>
    </div>
  ),
};

export const MedicalDashboard: Story = {
  render: () => (
    <div className="grid grid-cols-3 gap-4" style={{ width: 800 }}>
      <Card variant="default">
        <CardHeader title="Rawat Inap" />
        <CardBody>
          <div className="text-3xl font-bold text-teal-600">156</div>
          <p className="text-sm text-gray-500">Pasien aktif</p>
        </CardBody>
      </Card>

      <Card variant="default">
        <CardHeader title="IGD" />
        <CardBody>
          <div className="text-3xl font-bold text-orange-600">23</div>
          <p className="text-sm text-gray-500">Pasien dalam antrian</p>
        </CardBody>
      </Card>

      <Card variant="default">
        <CardHeader title="Rawat Jalan" />
        <CardBody>
          <div className="text-3xl font-bold text-blue-600">89</div>
          <p className="text-sm text-gray-500">Konsultasi hari ini</p>
        </CardBody>
      </Card>
    </div>
  ),
};

export const PatientCard: Story = {
  render: () => (
    <Card variant="interactive" style={{ width: 350 }}>
      <CardBody>
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-2xl">👤</span>
          </div>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-900">Siti Rahayu</h4>
            <p className="text-sm text-gray-500">RM-2024-0892 • 52 tahun</p>
            <div className="mt-2 flex gap-2">
              <span className="badge badge-primary">BPJS</span>
              <span className="badge badge-warning">Hipertensi</span>
            </div>
          </div>
        </div>
      </CardBody>
      <CardFooter>
        <div className="flex justify-between items-center w-full">
          <span className="text-xs text-gray-500">Terakhir: 15 Jan 2026</span>
          <button className="btn-sm btn-primary">Lihat</button>
        </div>
      </CardFooter>
    </Card>
  ),
};

export const LongContent: Story = {
  render: () => (
    <Card variant="default" style={{ width: 400 }}>
      <CardHeader title="Riwayat Medis" />
      <CardBody>
        <div className="space-y-3">
          <div className="pb-3 border-b border-gray-200">
            <p className="font-medium text-gray-900">20 Jan 2026</p>
            <p className="text-sm text-gray-600">Konsultasi Poli Penyakit Dalam</p>
            <p className="text-sm text-gray-500">Dr. Ahmad Sp.PD</p>
          </div>
          <div className="pb-3 border-b border-gray-200">
            <p className="font-medium text-gray-900">15 Jan 2026</p>
            <p className="text-sm text-gray-600">Pemeriksaan Laboratorium</p>
            <p className="text-sm text-gray-500">Hemoglobin, Gula Darah Puasa</p>
          </div>
          <div>
            <p className="font-medium text-gray-900">10 Jan 2026</p>
            <p className="text-sm text-gray-600">Konsultasi Poli Gigi</p>
            <p className="text-sm text-gray-500">Dr. Budi dgg.Sp.BM</p>
          </div>
        </div>
      </CardBody>
      <CardFooter>
        <button className="w-full btn-secondary">Lihat Semua Riwayat</button>
      </CardFooter>
    </Card>
  ),
};

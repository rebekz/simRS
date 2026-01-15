import type { Meta, StoryObj } from "@storybook/react";
import { CriticalAlert } from "./CriticalAlert";

const meta = {
  title: "Components/CriticalAlert",
  component: CriticalAlert,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    emergencyType: {
      control: "select",
      options: ["emergency", "critical", "code-blue", "code-red"],
    },
    pulse: { control: "boolean" },
  },
} satisfies Meta<typeof CriticalAlert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Emergency: Story = {
  args: {
    title: "Pasien dalam Kondisi Gawat",
    message: "Tekanan darah menurun drastis. Segera ke IGD!",
    emergencyType: "emergency",
    pulse: true,
  },
};

export const Critical: Story = {
  args: {
    title: "Kegagalan Sistem",
    message: "Sistem pendaftaran tidak dapat diakses. Gunakan manual.",
    emergencyType: "critical",
    pulse: true,
  },
};

export const CodeBlue: Story = {
  args: {
    title: "HENTI NAPAS - PASIEN JATUH",
    message: "Segera ke ruang resusitasi. Tim Code Blue diperlukan.",
    emergencyType: "code-blue",
    pulse: true,
  },
};

export const CodeRed: Story = {
  args: {
    title: "KEBAKARAN TERDETEKSI",
    message: "Evakuasi segera. Gunakan tangga darurat.",
    emergencyType: "code-red",
    pulse: true,
  },
};

export const NoPulse: Story = {
  args: {
    title: "Peringatan Sistem",
    message: "Backup sistem akan dimulai dalam 5 menit.",
    emergencyType: "critical",
    pulse: false,
  },
};

export const AllTypes: Story = {
  render: () => (
    <div className="flex flex-col gap-4 w-[500px]">
      <CriticalAlert
        title="KONDISI GAWAT DARURAT"
        message="Pasien memerlukan perhatian medis segera"
        emergencyType="emergency"
      />

      <CriticalAlert
        title="KEGAGALAN SISTEM KRITIS"
        message="Server database tidak merespons"
        emergencyType="critical"
      />

      <CriticalAlert
        title="CODE BLUE - HENTI JANTUNG"
        message="Pasien di Ruang 303 memerlukan resusitasi segera"
        emergencyType="code-blue"
      />

      <CriticalAlert
        title="CODE RED - KEBAKARAN"
        message="Lantai 2. Evakuasi segera"
        emergencyType="code-red"
      />
    </div>
  ),
};

export const MedicalEmergency: Story = {
  render: () => (
    <div className="w-[500px]">
      <CriticalAlert
        title="ANAFILAKSIS - REAKSI ALERGI PARAH"
        message="Pasien mengalami sesak napas, bengkak wajah, dan ruam setelah pemberian penisilin."
        emergencyType="code-blue"
      >
        <div className="mt-3 p-3 bg-white/50 rounded border border-blue-200">
          <p className="text-sm font-semibold text-blue-900">Tindakan Segera:</p>
          <ul className="text-sm text-blue-800 mt-1 space-y-1">
            <li>• Suntik Adrenalin 0.5mg IM</li>
            <li>• Panggil tim Code Blue</li>
            <li>• Siapkan oksigen dan akses IV</li>
            <li>• Pantau tanda vital tiap 2 menit</li>
          </ul>
        </div>
      </CriticalAlert>
    </div>
  ),
};

export const CardiacArrest: Story = {
  render: () => (
    <div className="w-[500px]">
      <CriticalAlert
        title="CARDIAC ARREST - PASIEN JATUH"
        message="Pasien di Poli Penyakit Dalam jatuh pingsan, tidak ada nadi dan napas."
        emergencyType="code-blue"
      >
        <div className="mt-3 space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <span className="font-semibold text-blue-900">Lokasi:</span>
            <span className="text-blue-800">Poli Penyakit Dalam, Ruang 205</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="font-semibold text-blue-900">Waktu:</span>
            <span className="text-blue-800" id="cardiac-timer">00:00</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <span className="font-semibold text-blue-900">Tim yang dipanggil:</span>
            <span className="text-blue-800">Dokter Jaga, Perawat, Resusitasi</span>
          </div>
        </div>
      </CriticalAlert>
    </div>
  ),
};

export const BPJSSystemFailure: Story = {
  render: () => (
    <div className="w-[500px]">
      <CriticalAlert
        title="BPJS VCLAIM API DOWN"
        message="Tidak dapat terhubung ke server BPJS. Verifikasi kepesertaan gagal."
        emergencyType="critical"
      >
        <div className="mt-3 space-y-2">
          <p className="text-sm text-gray-700">
            <strong>Alternatif:</strong>
          </p>
          <ol className="text-sm text-gray-700 list-decimal list-inside space-y-1">
            <li>Gunakan data manual dari kartu fisik pasien</li>
            <li>Minta pasien untuk membawa kartu BPJS asli</li>
            <li>Catat nomor BPJS manual untuk verifikasi nanti</li>
          </ol>
          <p className="text-sm text-gray-500 mt-2">
            Estimasi waktu recovery: 30-60 menit
          </p>
        </div>
      </CriticalAlert>
    </div>
  ),
};

export const DrugShortage: Story = {
  render: () => (
    <div className="w-[500px]">
      <CriticalAlert
        title="KEKOSONGAN OBAT KRITIS"
        message="Stok Adrenalin 1mg hampir habis. Sisa 5 ampul."
        emergencyType="critical"
        pulse={false}
      >
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-semibold text-gray-900">Obat:</span>
            <span className="text-gray-700">Adrenalin 1mg/1mL</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="font-semibold text-gray-900">Stok Saat Ini:</span>
            <span className="text-red-600 font-bold">5 ampul</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="font-semibold text-gray-900">Minimum Stok:</span>
            <span className="text-gray-700">20 ampul</span>
          </div>
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm text-yellow-900">
              <strong>Tindakan:</strong> Segera hubungi Farmasi untuk restock instan.
            </p>
          </div>
        </div>
      </CriticalAlert>
    </div>
  ),
};

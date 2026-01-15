import type { Meta, StoryObj } from "@storybook/react";
import { Alert } from "./Alert";

const meta = {
  title: "Components/Alert",
  component: Alert,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    variant: {
      control: "select",
      options: ["info", "success", "warning", "error"],
    },
    dismissible: { control: "boolean" },
  },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Info: Story = {
  args: {
    variant: "info",
    title: "Informasi",
    message: "Sistem akan melakukan maintenance pada pukul 22:00 WIB.",
  },
};

export const Success: Story = {
  args: {
    variant: "success",
    title: "Berhasil",
    message: "Data pasien telah berhasil disimpan.",
  },
};

export const Warning: Story = {
  args: {
    variant: "warning",
    title: "Peringatan",
    message: "BPJS pasien akan berakhir dalam 7 hari. Silakan verifikasi ulang.",
  },
};

export const Error: Story = {
  args: {
    variant: "error",
    title: "Gagal",
    message: "Gagal menyimpan data. Silakan periksa koneksi internet Anda.",
  },
};

export const Dismissible: Story = {
  args: {
    variant: "info",
    title: "Pemberitahuan",
    message: "Ini adalah pesan yang dapat ditutup.",
    dismissible: true,
  },
};

export const WithoutTitle: Story = {
  args: {
    variant: "info",
    message: "Pesan informasi sederhana tanpa judul.",
  },
};

export const CustomContent: Story = {
  args: {
    variant: "success",
    title: "Data Tersimpan",
    children: (
      <div>
        <p>Data pasien telah berhasil disimpan.</p>
        <p className="mt-2 text-xs">Nomor Rekam Medis: RM-2024-1234</p>
      </div>
    ),
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4 w-96">
      <Alert variant="info" title="Info" message="Informasi umum" />
      <Alert variant="success" title="Success" message="Operasi berhasil" />
      <Alert variant="warning" title="Warning" message="Peringatan penting" />
      <Alert variant="error" title="Error" message="Terjadi kesalahan" />
    </div>
  ),
};

export const MedicalContext: Story = {
  render: () => (
    <div className="flex flex-col gap-4 w-[500px]">
      <Alert
        variant="success"
        title="Pendaftaran Berhasil"
        message="Pasien telah terdaftar. Nomor antrian: A-023"
      />

      <Alert
        variant="warning"
        title="Alergi Obat Terdeteksi"
        message="Pasien memiliki alergi terhadap Penisilin. Harap berhati-hati dalam memberikan resep."
      />

      <Alert
        variant="error"
        title="BPJS Tidak Aktif"
        message="Keanggotaan BPJS pasien tidak aktif. Silakan verifikasi manual atau minta pasien untuk membayar biaya sendiri."
      />

      <Alert
        variant="info"
        title="Informasi Vaksinasi"
        message="Pasien belum menerima vaksin COVID-19 booster. Sarankan vaksinasi saat kunjungan."
      />
    </div>
  ),
};

export const DrugInteractionAlert: Story = {
  render: () => (
    <Alert
      variant="warning"
      title="Interaksi Obat Terdeteksi"
      dismissible
      message="Pasien sedang mengonsumsi Warfarin. Penggunaan NSAID dapat meningkatkan risiko perdarahan. Pertimbangkan alternatif lain."
    />
  ),
};

export const EmergencyAlert: Story = {
  render: () => (
    <Alert
      variant="error"
      title="KODE BIRU - GAWAT DARURAT"
      message="Pasien mengalami henti napas. Segera ke ruang kode biru. Tim resusitasi diperlukan segera."
    />
  ),
};

export const BPJSAlert: Story = {
  render: () => (
    <Alert
      variant="info"
      title="Verifikasi BPJS Berhasil"
      message="Peserta BPJS aktif. Faskes: RSUD Sehat Selalu. Kelas: 2. Masa berlaku sampai Desember 2026."
    />
  ),
};

export const SystemMaintenanceAlert: Story = {
  render: () => (
    <Alert
      variant="warning"
      title="Maintenance Terjadwal"
      dismissible
      message="Sistem akan melakukan maintenance pada Sabtu, 20 Januari 2026, pukul 22:00 - 02:00 WIB. Mohon simpan pekerjaan Anda sebelum waktu tersebut."
    />
  ),
};

export const CustomIcon: Story = {
  render: () => (
    <Alert
      variant="info"
      title="Dokumen Baru"
      icon={<span className="text-xl">📄</span>}
      message="Dokumen baru telah ditambahkan ke rekam medis pasien."
    />
  ),
};

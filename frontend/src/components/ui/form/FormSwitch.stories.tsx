import type { Meta, StoryObj } from "@storybook/react";
import { FormSwitch } from "./FormSwitch";

const meta = {
  title: "Components/Form/FormSwitch",
  component: FormSwitch,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    hint: { control: "text" },
    checked: { control: "boolean" },
    disabled: { control: "boolean" },
  },
} satisfies Meta<typeof FormSwitch>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "Aktifkan notifikasi",
  },
};

export const Checked: Story = {
  args: {
    label: "Pasien BPJS",
    checked: true,
    hint: "Pasien terdaftar sebagai peserta BPJS",
  },
};

export const WithHint: Story = {
  args: {
    label: "Verifikasi ELBPJS",
    hint: "Verifikasi kepesertaan BPJS secara elektronik",
  },
};

export const Disabled: Story = {
  args: {
    label: "Kirim SMS konfirmasi",
    checked: true,
    disabled: true,
    hint: "Layanan SMS sedang tidak tersedia",
  },
};

export const DisabledUnchecked: Story = {
  args: {
    label: "Fitur Premium",
    disabled: true,
    hint: "Upgrade ke premium untuk mengaktifkan",
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96">
      <FormSwitch label="Switch Normal" />
      <FormSwitch label="Switch Teraktif" checked />
      <FormSwitch
        label="Switch dengan Hint"
        hint="Petunjuk tambahan"
      />
      <FormSwitch
        label="Switch Disabled (Aktif)"
        checked
        disabled
      />
      <FormSwitch
        label="Switch Disabled (Nonaktif)"
        disabled
      />
    </div>
  ),
};

export const MedicalContext: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96 p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900">Pengaturan Pendaftaran</h3>

      <FormSwitch
        label="Pasien BPJS"
        checked
        hint="Verifikasi otomatis kepesertaan BPJS"
      />

      <FormSwitch
        label="Cetak SEP Otomatis"
        hint="Buat Surat Eligibility Peserta otomatis"
      />

      <FormSwitch
        label="Kirim Notifikasi"
        hint="Kirim SMS notifikasi ke pasien"
      />

      <FormSwitch
        label="Antrian Prioritas"
        hint="Tandai sebagai antrian prioritas (lansia/disabilitas)"
      />
    </div>
  ),
};

export const SettingsContext: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96 p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900">Pengaturan Akun</h3>

      <FormSwitch
        label="Dua Faktor Autentikasi (2FA)"
        hint="Tambahkan keamanan ekstra ke akun Anda"
      />

      <FormSwitch
        label="Notifikasi Email"
        checked
        hint="Terima update melalui email"
      />

      <FormSwitch
        label="Mode Gelap"
        hint="Gunakan tampilan gelap pada antarmuka"
      />

      <FormSwitch
        label="Simpan Riwayat Pencarian"
        checked
        hint="Simpan riwayat pencarian pasien"
      />
    </div>
  ),
};

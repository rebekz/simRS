import type { Meta, StoryObj } from "@storybook/react";
import { FormTextarea } from "./FormTextarea";

const meta = {
  title: "Components/Form/FormTextarea",
  component: FormTextarea,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    placeholder: { control: "text" },
    hint: { control: "text" },
    error: { control: "text" },
    required: { control: "boolean" },
    disabled: { control: "boolean" },
    autoResize: { control: "boolean" },
    rows: { control: "number" },
    maxLength: { control: "number" },
  },
} satisfies Meta<typeof FormTextarea>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "Catatan Medis",
    placeholder: "Masukkan catatan medis...",
    rows: 4,
  },
};

export const WithHint: Story = {
  args: {
    label: "Riwayat Penyakit",
    placeholder: "Jelaskan riwayat penyakit pasien...",
    hint: "Sertakan penyakit yang pernah diderita dan pengobatannya",
    rows: 5,
  },
};

export const WithError: Story = {
  args: {
    label: "Keluhan Utama",
    placeholder: "Deskripsikan keluhan pasien...",
    error: "Keluhan utama wajib diisi (minimal 10 karakter)",
    required: true,
    rows: 3,
  },
};

export const Required: Story = {
  args: {
    label: "Diagnosis Sementara",
    placeholder: "Masukkan diagnosis sementara...",
    required: true,
    hint: "Berdasarkan pemeriksaan fisik dan anamnesis",
    rows: 4,
  },
};

export const Disabled: Story = {
  args: {
    label: "Catatan Kunjungan Sebelumnya",
    value: "Pasien datang dengan keluhan demam tinggi selama 3 hari. Diberikan paracetamol 500mg dan disarankan istirahat.",
    disabled: true,
    rows: 4,
    hint: "Catatan dari kunjungan terakhir (read-only)",
  },
};

export const WithMaxLength: Story = {
  args: {
    label: "Alergi Obat",
    placeholder: "Sebutkan obat yang menyebabkan alergi...",
    maxLength: 500,
    hint: "Maksimal 500 karakter",
    rows: 3,
  },
};

export const AutoResizeDisabled: Story = {
  args: {
    label: "Resep Dokter",
    placeholder: "Tulis resep di sini...",
    autoResize: false,
    rows: 6,
    hint: "Drag handle di pojok kanan bawah untuk mengubah ukuran",
  },
};

export const LongContent: Story = {
  args: {
    label: "SOAP Note - Subjective",
    value: "Pasien laki-laki 45 tahun datang dengan keluhan nyeri dada kiri yang dirasakan sejak 2 hari lalu. Nyeri dirasakan seperti tertekan, menetap, dan memburuk saat aktivitas fisik. Pasien mengeluh sesak napas ringan terutama saat naik tangga. Tidak ada keluhan mual, muntah, atau keringat dingin. Riwayat penyakit jantung dalam keluarga tidak diketahui. Pasien adalah perokok aktif sejak 20 tahun terakhir, rata-rata 10 batang per hari.",
    rows: 6,
    autoResize: true,
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96">
      <FormTextarea
        label="Textarea Normal"
        placeholder="Contoh textarea normal"
        rows={4}
      />
      <FormTextarea
        label="Textarea dengan Hint"
        placeholder="Contoh textarea"
        hint="Petunjuk tambahan"
        rows={4}
      />
      <FormTextarea
        label="Textarea Error"
        placeholder="Contoh textarea error"
        error="Nilai ini terlalu singkat"
        rows={3}
      />
      <FormTextarea
        label="Textarea Disabled"
        value="Konten yang tidak dapat diubah"
        disabled
        rows={4}
      />
      <FormTextarea
        label="Textarea Required"
        placeholder="Wajib diisi"
        required
        rows={4}
      />
    </div>
  ),
};

export const MedicalContext: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-[500px] p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900">Catatan Perkembangan Pasien</h3>

      <FormTextarea
        label="Subjective (S)"
        placeholder="Keluhan pasien..."
        rows={3}
        hint="Apa yang dikatakan pasien"
      />

      <FormTextarea
        label="Objective (O)"
        placeholder="Hasil pemeriksaan fisik..."
        rows={3}
        hint="Data dari pemeriksaan objektif"
      />

      <FormTextarea
        label="Assessment (A)"
        placeholder="Diagnosis sementara..."
        rows={3}
        required
        hint="Interpretasi medis"
      />

      <FormTextarea
        label="Plan (P)"
        placeholder="Rencana tatalaksana..."
        rows={3}
        hint="Rencana perawatan dan pengobatan"
      />
    </div>
  ),
};

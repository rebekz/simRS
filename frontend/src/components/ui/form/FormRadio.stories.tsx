import type { Meta, StoryObj } from "@storybook/react";
import { FormRadio } from "./FormRadio";

const meta = {
  title: "Components/Form/FormRadio",
  component: FormRadio,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    hint: { control: "text" },
    error: { control: "text" },
    disabled: { control: "boolean" },
    required: { control: "boolean" },
    options: { control: "object" },
  },
} satisfies Meta<typeof FormRadio>;

export default meta;
type Story = StoryObj<typeof meta>;

const genderOptions = [
  { value: "male", label: "Laki-laki" },
  { value: "female", label: "Perempuan" },
];

const urgencyOptions = [
  { value: "routine", label: "Biasa (Routine)" },
  { value: "urgent", label: "Segera (Urgent)" },
  { value: "emergency", label: "Gawat Darurat (Emergency)" },
];

const paymentOptions = [
  { value: "bpjs", label: "BPJS Kesehatan" },
  { value: "asuransi", label: "Asuransi Swasta" },
  { value: "perusahaan", label: "Perusahaan" },
  { value: "biaya_sendiri", label: "Biaya Sendiri" },
];

export const Default: Story = {
  args: {
    label: "Jenis Kelamin",
    name: "gender",
    options: genderOptions,
  },
};

export const WithHint: Story = {
  args: {
    label: "Tingkat Urgensi",
    name: "urgency",
    options: urgencyOptions,
    hint: "Pilih tingkat urgensi pemeriksaan",
    value: "routine",
  },
};

export const WithError: Story = {
  args: {
    label: "Cara Pembayaran",
    name: "payment",
    options: paymentOptions,
    error: "Silakan pilih cara pembayaran",
    required: true,
  },
};

export const Required: Story = {
  args: {
    label: "Status Pasien",
    name: "status",
    options: [
      { value: "baru", label: "Pasien Baru" },
      { value: "lama", label: "Pasien Lama" },
    ],
    required: true,
  },
};

export const Disabled: Story = {
  args: {
    label: "Kelas Rawat Inap",
    name: "class",
    options: [
      { value: "vvip", label: "VVIP" },
      { value: "vip", label: "VIP" },
      { value: "1", label: "Kelas 1" },
      { value: "2", label: "Kelas 2" },
      { value: "3", label: "Kelas 3" },
    ],
    value: "3",
    disabled: true,
    hint: "Kelas telah ditetapkan",
  },
};

export const Vertical: Story = {
  args: {
    label: "Poli Tujuan",
    name: "poly",
    options: [
      { value: "umum", label: "Poli Umum" },
      { value: "anak", label: "Poli Anak" },
      { value: "gigi", label: "Poli Gigi" },
      { value: "mata", label: "Poli Mata" },
    ],
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-8 w-96">
      <FormRadio
        label="Radio Normal"
        name="demo1"
        options={genderOptions}
      />
      <FormRadio
        label="Radio dengan Hint"
        name="demo2"
        options={urgencyOptions}
        hint="Pilih salah satu opsi"
      />
      <FormRadio
        label="Radio Error"
        name="demo3"
        options={paymentOptions}
        error="Pilihan wajib dipilih"
        required
      />
      <FormRadio
        label="Radio Disabled"
        name="demo4"
        options={genderOptions}
        value="male"
        disabled
      />
    </div>
  ),
};

export const MedicalContext: Story = {
  render: () => (
    <div className="flex flex-col gap-8 w-96 p-6 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900">Form Pendaftaran</h3>

      <FormRadio
        label="Jenis Kelamin"
        name="gender"
        options={genderOptions}
        required
      />

      <FormRadio
        label="Tingkat Urgensi"
        name="urgency"
        options={urgencyOptions}
        hint="Pilih sesuai kondisi pasien"
        value="routine"
      />

      <FormRadio
        label="Cara Pembayaran"
        name="payment"
        options={paymentOptions}
        required
      />
    </div>
  ),
};

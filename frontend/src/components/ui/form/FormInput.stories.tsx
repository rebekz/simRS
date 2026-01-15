import type { Meta, StoryObj } from "@storybook/react";
import { FormInput } from "./FormInput";

const meta = {
  title: "Components/Form/FormInput",
  component: FormInput,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    type: {
      control: "select",
      options: ["text", "email", "password", "number", "tel", "date", "time"],
    },
    label: { control: "text" },
    placeholder: { control: "text" },
    hint: { control: "text" },
    error: { control: "text" },
    required: { control: "boolean" },
    disabled: { control: "boolean" },
  },
} satisfies Meta<typeof FormInput>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "Nama Lengkap",
    placeholder: "Masukkan nama lengkap",
  },
};

export const WithHint: Story = {
  args: {
    label: "Email",
    type: "email",
    placeholder: "nama@email.com",
    hint: "Kami akan mengirimkan konfirmasi ke email ini",
  },
};

export const WithError: Story = {
  args: {
    label: "NIK",
    placeholder: "16 digit NIK",
    error: "NIK harus 16 digit angka",
    required: true,
  },
};

export const Required: Story = {
  args: {
    label: "Nomor BPJS",
    placeholder: "13 digit nomor BPJS",
    required: true,
    hint: "Wajib diisi untuk pasien BPJS",
  },
};

export const Disabled: Story = {
  args: {
    label: "Nomor Rekam Medis",
    value: "RM-2024-1234",
    disabled: true,
    hint: "Otomatis dihasilkan oleh sistem",
  },
};

export const Password: Story = {
  args: {
    label: "Kata Sandi",
    type: "password",
    placeholder: "Masukkan kata sandi",
    required: true,
    hint: "Minimal 8 karakter",
  },
};

export const NumberInput: Story = {
  args: {
    label: "Usia",
    type: "number",
    placeholder: "0",
    min: 0,
    max: 150,
  },
};

export const DateInput: Story = {
  args: {
    label: "Tanggal Lahir",
    type: "date",
    required: true,
  },
};

export const TelInput: Story = {
  args: {
    label: "Nomor Telepon",
    type: "tel",
    placeholder: "081234567890",
    hint: "Format Indonesia (08...)",
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96">
      <FormInput
        label="Input Normal"
        placeholder="Contoh input normal"
      />
      <FormInput
        label="Input dengan Hint"
        placeholder="Contoh input"
        hint="Ini adalah petunjuk tambahan"
      />
      <FormInput
        label="Input Error"
        placeholder="Contoh input error"
        error="Nilai ini tidak valid"
      />
      <FormInput
        label="Input Disabled"
        value="Tidak bisa diubah"
        disabled
      />
      <FormInput
        label="Input Required"
        placeholder="Wajib diisi"
        required
      />
    </div>
  ),
};

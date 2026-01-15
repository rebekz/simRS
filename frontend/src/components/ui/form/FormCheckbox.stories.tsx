import type { Meta, StoryObj } from "@storybook/react";
import { FormCheckbox } from "./FormCheckbox";

const meta = {
  title: "Components/Form/FormCheckbox",
  component: FormCheckbox,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    label: { control: "text" },
    hint: { control: "text" },
    error: { control: "text" },
    checked: { control: "boolean" },
    disabled: { control: "boolean" },
    required: { control: "boolean" },
  },
} satisfies Meta<typeof FormCheckbox>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    label: "Saya menyetujui syarat dan ketentuan",
  },
};

export const Checked: Story = {
  args: {
    label: "Pasien memiliki BPJS",
    checked: true,
  },
};

export const WithHint: Story = {
  args: {
    label: "Pasien memiliki alergi obat",
    hint: "Centang jika pasien memiliki riwayat alergi",
  },
};

export const Required: Story = {
  args: {
    label: "Saya menyetujui pemrosesan data medis",
    required: true,
    hint: "Wajib disetujui untuk melanjutkan",
  },
};

export const Disabled: Story = {
  args: {
    label: "Pasien sudah melakukan check-in",
    checked: true,
    disabled: true,
  },
};

export const DisabledUnchecked: Story = {
  args: {
    label: "Pilihan tidak tersedia",
    disabled: true,
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96">
      <FormCheckbox label="Checkbox Normal" />
      <FormCheckbox label="Checkbox Tercentang" checked />
      <FormCheckbox
        label="Checkbox dengan Hint"
        hint="Petunjuk tambahan"
      />
      <FormCheckbox
        label="Checkbox Wajib"
        required
      />
      <FormCheckbox
        label="Checkbox Disabled (Checked)"
        checked
        disabled
      />
      <FormCheckbox
        label="Checkbox Disabled (Unchecked)"
        disabled
      />
    </div>
  ),
};

export const CheckboxGroup: Story = {
  render: () => (
    <div className="flex flex-col gap-4 w-96">
      <h3 className="font-medium text-gray-900">Gejala yang Dialami</h3>
      <FormCheckbox label="Demam" />
      <FormCheckbox label="Batuk" />
      <FormCheckbox label="Sesak Napas" />
      <FormCheckbox label="Sakit Tenggorokan" />
      <FormCheckbox label="Sakit Kepala" />
      <FormCheckbox label="Nyeri Otot" />
      <FormCheckbox label="Hilang Indra Perasa/Penciuman" />
    </div>
  ),
};

import type { Meta, StoryObj } from "@storybook/react";
import { FormSelect } from "./FormSelect";

const meta = {
  title: "Components/Form/FormSelect",
  component: FormSelect,
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
    options: { control: "object" },
  },
} satisfies Meta<typeof FormSelect>;

export default meta;
type Story = StoryObj<typeof meta>;

const genderOptions = [
  { value: "male", label: "Laki-laki" },
  { value: "female", label: "Perempuan" },
];

const bloodTypeOptions = [
  { value: "A", label: "A" },
  { value: "B", label: "B" },
  { value: "AB", label: "AB" },
  { value: "O", label: "O" },
];

const departmentOptions = [
  { value: "", label: "Pilih Departemen" },
  { value: "igd", label: "Instalasi Gawat Darurat (IGD)" },
  { value: "rawat_inap", label: "Rawat Inap" },
  { value: "rawat_jalan", label: "Rawat Jalan" },
  { value: "farmasi", label: "Farmasi" },
  { value: "laboratorium", label: "Laboratorium" },
  { value: "radiologi", label: "Radiologi" },
];

const bpjsClassOptions = [
  { value: "1", label: "Kelas 1" },
  { value: "2", label: "Kelas 2" },
  { value: "3", label: "Kelas 3" },
];

export const Default: Story = {
  args: {
    label: "Jenis Kelamin",
    placeholder: "Pilih jenis kelamin",
    options: genderOptions,
  },
};

export const WithHint: Story = {
  args: {
    label: "Golongan Darah",
    placeholder: "Pilih golongan darah",
    options: bloodTypeOptions,
    hint: "Diperlukan untuk transfusi darah",
  },
};

export const WithError: Story = {
  args: {
    label: "Departemen",
    placeholder: "Pilih departemen",
    options: departmentOptions,
    error: "Silakan pilih departemen tujuan",
    required: true,
  },
};

export const Required: Story = {
  args: {
    label: "Kelas BPJS",
    placeholder: "Pilih kelas",
    options: bpjsClassOptions,
    required: true,
  },
};

export const Disabled: Story = {
  args: {
    label: "Status Pasien",
    value: "rawat_inap",
    options: [
      { value: "rawat_inap", label: "Rawat Inap" },
      { value: "rawat_jalan", label: "Rawat Jalan" },
    ],
    disabled: true,
    hint: "Status tidak dapat diubah",
  },
};

export const WithDisabledOptions: Story = {
  args: {
    label: "Poli Tujuan",
    placeholder: "Pilih poli",
    options: [
      { value: "umum", label: "Poli Umum" },
      { value: "anak", label: "Poli Anak" },
      { value: "full", label: "Poli Penyakit Dalam (Penuh)", disabled: true },
      { value: "bedah", label: "Poli Bedah" },
    ],
  },
};

export const LongList: Story = {
  args: {
    label: "Provinsi",
    placeholder: "Pilih provinsi",
    options: [
      { value: "aceh", label: "Aceh" },
      { value: "sumut", label: "Sumatera Utara" },
      { value: "sumbar", label: "Sumatera Barat" },
      { value: "riau", label: "Riau" },
      { value: "kepri", label: "Kepulauan Riau" },
      { value: "jambi", label: "Jambi" },
      { value: "sumsel", label: "Sumatera Selatan" },
      { value: "bengkulu", label: "Bengkulu" },
      { value: "lampung", label: "Lampung" },
      { value: "dki", label: "DKI Jakarta" },
      { value: "jabar", label: "Jawa Barat" },
      { value: "jateng", label: "Jawa Tengah" },
      { value: "diy", label: "D.I. Yogyakarta" },
      { value: "jatim", label: "Jawa Timur" },
      { value: "banten", label: "Banten" },
      { value: "bali", label: "Bali" },
    ],
  },
};

export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-6 w-96">
      <FormSelect
        label="Select Normal"
        placeholder="Pilih opsi"
        options={genderOptions}
      />
      <FormSelect
        label="Select dengan Hint"
        placeholder="Pilih opsi"
        options={bloodTypeOptions}
        hint="Petunjuk tambahan"
      />
      <FormSelect
        label="Select Error"
        placeholder="Pilih opsi"
        options={departmentOptions}
        error="Pilihan tidak valid"
      />
      <FormSelect
        label="Select Disabled"
        value="igd"
        options={departmentOptions}
        disabled
      />
      <FormSelect
        label="Select Required"
        placeholder="Pilih opsi"
        options={bpjsClassOptions}
        required
      />
    </div>
  ),
};

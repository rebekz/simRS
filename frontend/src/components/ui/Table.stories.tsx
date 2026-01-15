import type { Meta, StoryObj } from "@storybook/react";
import { Table } from "./Table";
import { Badge } from "./Badge";

const meta = {
  title: "Components/Table",
  component: Table,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    sortable: { control: "boolean" },
  },
} satisfies Meta<typeof Table>;

export default meta;
type Story = StoryObj<typeof meta>;

interface Patient {
  id: string;
  name: string;
  rmNumber: string;
  age: number;
  gender: string;
  status: string;
}

const patientData: Patient[] = [
  { id: "1", name: "Ahmad Susanto", rmNumber: "RM-2024-0001", age: 45, gender: "Laki-laki", status: "Rawat Inap" },
  { id: "2", name: "Siti Rahayu", rmNumber: "RM-2024-0002", age: 52, gender: "Perempuan", status: "Rawat Jalan" },
  { id: "3", name: "Budi Pratama", rmNumber: "RM-2024-0003", age: 38, gender: "Laki-laki", status: "IGD" },
  { id: "4", name: "Dewi Lestari", rmNumber: "RM-2024-0004", age: 29, gender: "Perempuan", status: "Rawat Jalan" },
  { id: "5", name: "Eko Kurniawan", rmNumber: "RM-2024-0005", age: 61, gender: "Laki-laki", status: "Rawat Inap" },
];

const patientColumns = [
  { key: "name", title: "Nama Pasien" },
  { key: "rmNumber", title: "No. RM" },
  { key: "age", title: "Usia" },
  { key: "gender", title: "Jenis Kelamin" },
  { key: "status", title: "Status" },
];

export const Default: Story = {
  args: {
    data: patientData,
    columns: patientColumns,
  },
};

export const Sortable: Story = {
  args: {
    data: patientData,
    columns: patientColumns,
    sortable: true,
  },
};

export const WithCustomRender: Story = {
  args: {
    data: patientData,
    columns: [
      { key: "name", title: "Nama Pasien" },
      { key: "rmNumber", title: "No. RM" },
      {
        key: "age",
        title: "Usia",
        render: (value: any) => `${value} tahun`,
      },
      { key: "gender", title: "Jenis Kelamin" },
      {
        key: "status",
        title: "Status",
        render: (value: any) => {
          const variant = value === "Rawat Inap" ? "success" : value === "IGD" ? "error" : "primary";
          return <Badge variant={variant}>{value}</Badge>;
        },
      },
    ],
  },
};

export const Empty: Story = {
  args: {
    data: [],
    columns: patientColumns,
  },
};

interface Appointment {
  id: string;
  time: string;
  patient: string;
  doctor: string;
  type: string;
  status: string;
}

const appointmentData: Appointment[] = [
  { id: "1", time: "08:00", patient: "Ahmad Susanto", doctor: "dr. Budi Sp.PD", type: "Konsultasi", status: "Selesai" },
  { id: "2", time: "09:00", patient: "Siti Rahayu", doctor: "dr. Ani Sp.A", type: "Konsultasi", status: "Dalam Pemeriksaan" },
  { id: "3", time: "10:00", patient: "Eko Prasetyo", doctor: "dr. Candra Sp.B", type: "Konsultasi", status: "Menunggu" },
  { id: "4", time: "11:00", patient: "Dewi Anggraini", doctor: "dr. Dedi Sp.JP", type: "Follow-up", status: "Menunggu" },
];

export const Appointments: Story = {
  render: () => (
    <Table
      data={appointmentData}
      columns={[
        { key: "time", title: "Jam" },
        { key: "patient", title: "Pasien" },
        { key: "doctor", title: "Dokter" },
        { key: "type", title: "Jenis" },
        {
          key: "status",
          title: "Status",
          render: (value) => {
            const variant = value === "Selesai" ? "success" : value === "Dalam Pemeriksaan" ? "warning" : "neutral";
            return <Badge variant={variant}>{value}</Badge>;
          },
        },
      ]}
      sortable
    />
  ),
};

interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  stock: number;
}

const medicationData: Medication[] = [
  { id: "1", name: "Paracetamol 500mg", dosage: "500mg", frequency: "3x sehari", stock: 1500 },
  { id: "2", name: "Amoxicillin 500mg", dosage: "500mg", frequency: "3x sehari", stock: 45 },
  { id: "3", name: "Omeprazole 20mg", dosage: "20mg", frequency: "1x sehari", stock: 8 },
  { id: "4", name: "Cetirizine 10mg", dosage: "10mg", frequency: "1x sehari", stock: 320 },
];

export const MedicationInventory: Story = {
  render: () => (
    <Table
      data={medicationData}
      columns={[
        { key: "name", title: "Nama Obat" },
        { key: "dosage", title: "Dosis" },
        { key: "frequency", title: "Frekuensi" },
        {
          key: "stock",
          title: "Stok",
          render: (value) => {
            const variant = value > 100 ? "success" : value > 50 ? "warning" : "error";
            return <Badge variant={variant}>{value} unit</Badge>;
          },
        },
      ]}
      sortable
    />
  ),
};

interface Vitals {
  id: string;
  datetime: string;
  bp: string;
  hr: number;
  temp: number;
  spo2: number;
}

const vitalsData: Vitals[] = [
  { id: "1", datetime: "16 Jan 2026 08:00", bp: "120/80", hr: 72, temp: 36.5, spo2: 98 },
  { id: "2", datetime: "16 Jan 2026 12:00", bp: "125/82", hr: 78, temp: 36.7, spo2: 97 },
  { id: "3", datetime: "16 Jan 2026 16:00", bp: "118/78", hr: 75, temp: 36.6, spo2: 98 },
];

export const VitalSigns: Story = {
  render: () => (
    <Table
      data={vitalsData}
      columns={[
        { key: "datetime", title: "Waktu" },
        { key: "bp", title: "Tekanan Darah" },
        { key: "hr", title: "Nadi (/menit)" },
        { key: "temp", title: "Suhu (°C)" },
        { key: "spo2", title: "SpO2 (%)" },
      ]}
    />
  ),
};

export const WideTable: Story = {
  render: () => (
    <div style={{ width: 900 }}>
      <Table
        data={patientData}
        columns={[
          { key: "rmNumber", title: "No. RM" },
          { key: "name", title: "Nama Lengkap" },
          { key: "nik", title: "NIK" },
          { key: "age", title: "Usia" },
          { key: "gender", title: "Jenis Kelamin" },
          { key: "bpjs", title: "BPJS" },
          { key: "phone", title: "Telepon" },
          { key: "address", title: "Alamat" },
        ]}
        sortable
      />
    </div>
  ),
};

export const PatientTable: Story = {
  render: () => (
    <Table
      data={patientData}
      columns={[
        {
          key: "name",
          title: "Nama Pasien",
          render: (value) => (
            <div className="font-medium text-gray-900">{value}</div>
          ),
        },
        { key: "rmNumber", title: "No. RM" },
        { key: "age", title: "Usia", render: (value) => `${value} th` },
        { key: "gender", title: "L/P" },
        {
          key: "status",
          title: "Status",
          render: (value) => {
            const variant = value === "Rawat Inap" ? "success" : value === "IGD" ? "error" : "primary";
            return <Badge variant={variant}>{value}</Badge>;
          },
        },
      ]}
      sortable
    />
  ),
};

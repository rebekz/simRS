import type { Meta, StoryObj } from "@storybook/react";
import { PatientCard } from "./PatientCard";

const meta = {
  title: "Components/PatientCard",
  component: PatientCard,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
  argTypes: {
    showBPJS: { control: "boolean" },
  },
} satisfies Meta<typeof PatientCard>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockPatient = {
  id: "1",
  name: "Ahmad Susanto",
  rmNumber: "RM-2024-1234",
  isBPJS: true,
  bpjsNumber: "1234567890",
};

const mockPatientWithPhoto = {
  id: "2",
  name: "Siti Rahayu",
  rmNumber: "RM-2024-5678",
  photoUrl: "https://i.pravatar.cc/150?img=5",
  isBPJS: true,
  bpjsNumber: "0987654321",
};

const mockPatientNonBPJS = {
  id: "3",
  name: "Budi Pratama",
  rmNumber: "RM-2024-9012",
  isBPJS: false,
};

export const Default: Story = {
  args: {
    patient: mockPatient,
  },
};

export const WithPhoto: Story = {
  args: {
    patient: mockPatientWithPhoto,
  },
};

export const NonBPJS: Story = {
  render: () => (
    <div style={{ width: 350 }}>
      <PatientCard patient={mockPatientNonBPJS} />
    </div>
  ),
};

export const HideBPJS: Story = {
  render: () => (
    <div style={{ width: 350 }}>
      <PatientCard patient={mockPatient} showBPJS={false} />
    </div>
  ),
};

export const Clickable: Story = {
  args: {
    patient: mockPatient,
    onClick: () => alert("Navigasi ke detail pasien"),
  },
};

export const AllVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4" style={{ width: 350 }}>
      <PatientCard patient={mockPatient} />

      <PatientCard patient={mockPatientWithPhoto} />

      <PatientCard patient={mockPatientNonBPJS} />

      <PatientCard patient={mockPatient} showBPJS={false} />
    </div>
  ),
};

export const PatientList: Story = {
  render: () => (
    <div className="space-y-3" style={{ width: 400 }}>
      <h3 className="font-semibold text-gray-900">Pasien Terbaru</h3>

      <PatientCard
        patient={{
          id: "1",
          name: "Ahmad Susanto",
          rmNumber: "RM-2024-1234",
          isBPJS: true,
          bpjsNumber: "1234567890",
        }}
      />

      <PatientCard
        patient={{
          id: "2",
          name: "Siti Rahayu",
          rmNumber: "RM-2024-5678",
          isBPJS: true,
          bpjsNumber: "0987654321",
        }}
      />

      <PatientCard
        patient={{
          id: "3",
          name: "Budi Pratama",
          rmNumber: "RM-2024-9012",
          isBPJS: false,
        }}
      />

      <PatientCard
        patient={{
          id: "4",
          name: "Dewi Anggraini",
          rmNumber: "RM-2024-3456",
          isBPJS: true,
          bpjsNumber: "5678901234",
        }}
      />
    </div>
  ),
};

export const DifferentClasses: Story = {
  render: () => (
    <div className="grid grid-cols-3 gap-4">
      <div>
        <p className="text-sm text-gray-600 mb-2">Kelas 1</p>
        <PatientCard
          patient={{
            id: "1",
            name: "Ahmad Wijaya",
            rmNumber: "RM-2024-0001",
            isBPJS: true,
            bpjsNumber: "1111111111",
          }}
        />
      </div>

      <div>
        <p className="text-sm text-gray-600 mb-2">Kelas 2</p>
        <PatientCard
          patient={{
            id: "2",
            name: "Suti Rahayu",
            rmNumber: "RM-2024-0002",
            isBPJS: true,
            bpjsNumber: "2222222222",
          }}
        />
      </div>

      <div>
        <p className="text-sm text-gray-600 mb-2">Kelas 3</p>
        <PatientCard
          patient={{
            id: "3",
            name: "Budi Santoso",
            rmNumber: "RM-2024-0003",
            isBPJS: true,
            bpjsNumber: "3333333333",
          }}
        />
      </div>
    </div>
  ),
};

export const LongNames: Story = {
  render: () => (
    <div className="space-y-3" style={{ width: 350 }}>
      <PatientCard
        patient={{
          id: "1",
          name: "Dr. Muhammad Hafiz Ibrahim Al-Farisi Sp.PD",
          rmNumber: "RM-2024-0001",
          isBPJS: true,
        }}
      />

      <PatientCard
        patient={{
          id: "2",
          name: "Nyonya Siti Aminah Binti Abdul Rahman Al-Haddad",
          rmNumber: "RM-2024-0002",
          isBPJS: false,
        }}
      />
    </div>
  ),
};

export const WithActions: Story = {
  render: () => (
    <div className="space-y-3" style={{ width: 400 }}>
      <PatientCard
        patient={mockPatient}
        onClick={() => alert("Navigasi ke detail pasien")}
      />
      <PatientCard
        patient={mockPatientWithPhoto}
        onClick={() => alert("Navigasi ke detail pasien")}
      />
    </div>
  ),
};

export const CompactView: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-3">
      <PatientCard patient={mockPatient} variant="default" />
      <PatientCard patient={mockPatientNonBPJS} variant="default" />
      <PatientCard patient={mockPatientWithPhoto} variant="default" />
      <PatientCard
        patient={{
          id: "4",
          name: "Eko Prasetyo",
          rmNumber: "RM-2024-8888",
          isBPJS: true,
          bpjsNumber: "8888888888",
        }}
        variant="default"
      />
    </div>
  ),
};

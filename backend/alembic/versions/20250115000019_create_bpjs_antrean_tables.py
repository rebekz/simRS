"""create BPJS Antrean tables

Revision ID: 20250115000019
Revises: 20250114000018
Create Date: 2026-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250115000019'
down_revision = '20250114000018'
branch_labels = None
depends_on = None


def upgrade():
    # Create bpjs_antrean_sync_logs table
    op.create_table(
        'bpjs_antrean_sync_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False, comment='Endpoint API BPJS yang dipanggil'),
        sa.Column('http_method', sa.String(length=10), nullable=False, comment='HTTP method (GET, POST, PUT, DELETE)'),
        sa.Column('request_payload', postgresql.JSON(), nullable=True, comment='Payload request yang dikirim ke API BPJS'),
        sa.Column('response_payload', postgresql.JSON(), nullable=True, comment='Response yang diterima dari API BPJS'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Status sinkronisasi (success, failed, pending)'),
        sa.Column('http_status_code', sa.Integer(), nullable=True, comment='HTTP status code dari response'),
        sa.Column('bpjs_response_code', sa.String(length=20), nullable=True, comment='Kode response spesifik dari BPJS'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Pesan error jika terjadi kegagalan'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0', comment='Jumlah percobaan ulang'),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True, comment='Waktu eksekusi dalam milidetik'),
        sa.Column('referenced_entity_type', sa.String(length=50), nullable=True, comment='Tipe entitas yang terkait (booking, task, dll)'),
        sa.Column('referenced_entity_id', sa.Integer(), nullable=True, comment='ID entitas yang terkait'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp pembuatan record'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp update terakhir record'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bpjs_antrean_sync_logs_endpoint', 'bpjs_antrean_sync_logs', ['endpoint'])
    op.create_index('ix_bpjs_antrean_sync_logs_status', 'bpjs_antrean_sync_logs', ['status'])
    op.create_index('ix_bpjs_antrean_sync_logs_created_at', 'bpjs_antrean_sync_logs', ['created_at'])
    op.create_index('ix_bpjs_antrean_sync_logs_referenced_entity', 'bpjs_antrean_sync_logs', ['referenced_entity_type', 'referenced_entity_id'])

    # Create bpjs_antrean_bookings table
    op.create_table(
        'bpjs_antrean_bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_code', sa.String(length=100), nullable=False, comment='Kode booking dari BPJS'),
        sa.Column('appointment_id', sa.Integer(), nullable=True, comment='Referensi ke appointment internal'),
        sa.Column('patient_id', sa.Integer(), nullable=False, comment='Referensi ke pasien'),
        sa.Column('poli_id', sa.Integer(), nullable=False, comment='Referensi ke poli'),
        sa.Column('doctor_id', sa.Integer(), nullable=True, comment='Referensi ke dokter'),
        sa.Column('booking_date', sa.DateTime(timezone=True), nullable=False, comment='Tanggal dan waktu booking'),
        sa.Column('booking_time', sa.Time(), nullable=False, comment='Waktu booking'),
        sa.Column('estimated_time', sa.DateTime(timezone=True), nullable=True, comment='Perkiraan waktu pelayanan'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='booked', comment='Status booking (booked, checked-in, serving, completed, cancelled)'),
        sa.Column('bpjs_task_id', sa.Integer(), nullable=True, comment='ID tugas dari sistem BPJS'),
        sa.Column('referral_number', sa.String(length=100), nullable=True, comment='Nomor rujukan BPJS'),
        sa.Column('sep_number', sa.String(length=50), nullable=True, comment='Nomor SEP (Surat Eligibilitas Peserta)'),
        sa.Column('checkin_time', sa.DateTime(timezone=True), nullable=True, comment='Waktu check-in pasien'),
        sa.Column('service_start_time', sa.DateTime(timezone=True), nullable=True, comment='Waktu mulai pelayanan'),
        sa.Column('service_end_time', sa.DateTime(timezone=True), nullable=True, comment='Waktu selesai pelayanan'),
        sa.Column('sync_status', sa.String(length=20), nullable=False, server_default='pending', comment='Status sinkronisasi dengan BPJS'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp sinkronisasi terakhir'),
        sa.Column('sync_error_message', sa.Text(), nullable=True, comment='Pesan error dari sinkronisasi BPJS'),
        sa.Column('bpjs_response_data', postgresql.JSON(), nullable=True, comment='Response data lengkap dari BPJS'),
        sa.Column('cancellation_reason', sa.Text(), nullable=True, comment='Alasan pembatalan booking'),
        sa.Column('cancelled_by', sa.Integer(), nullable=True, comment='User yang membatalkan'),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp pembatalan'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp pembuatan record'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp update terakhir record'),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], name='fk_bpjs_antrean_bookings_appointment_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='fk_bpjs_antrean_bookings_patient_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['poli_id'], ['polis.id'], name='fk_bpjs_antrean_bookings_poli_id', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['doctor_id'], ['doctors.id'], name='fk_bpjs_antrean_bookings_doctor_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['cancelled_by'], ['users.id'], name='fk_bpjs_antrean_bookings_cancelled_by', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('booking_code')
    )
    op.create_index('ix_bpjs_antrean_bookings_id', 'bpjs_antrean_bookings', ['id'])
    op.create_index('ix_bpjs_antrean_bookings_booking_code', 'bpjs_antrean_bookings', ['booking_code'])
    op.create_index('ix_bpjs_antrean_bookings_appointment_id', 'bpjs_antrean_bookings', ['appointment_id'])
    op.create_index('ix_bpjs_antrean_bookings_patient_id', 'bpjs_antrean_bookings', ['patient_id'])
    op.create_index('ix_bpjs_antrean_bookings_poli_id', 'bpjs_antrean_bookings', ['poli_id'])
    op.create_index('ix_bpjs_antrean_bookings_doctor_id', 'bpjs_antrean_bookings', ['doctor_id'])
    op.create_index('ix_bpjs_antrean_bookings_booking_date', 'bpjs_antrean_bookings', ['booking_date'])
    op.create_index('ix_bpjs_antrean_bookings_status', 'bpjs_antrean_bookings', ['status'])
    op.create_index('ix_bpjs_antrean_bookings_bpjs_task_id', 'bpjs_antrean_bookings', ['bpjs_task_id'])
    op.create_index('ix_bpjs_antrean_bookings_referral_number', 'bpjs_antrean_bookings', ['referral_number'])
    op.create_index('ix_bpjs_antrean_bookings_sep_number', 'bpjs_antrean_bookings', ['sep_number'])

    # Create bpjs_antrean_tasks table
    op.create_table(
        'bpjs_antrean_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False, comment='Referensi ke booking BPJS'),
        sa.Column('task_id', sa.String(length=100), nullable=False, comment='ID tugas dari sistem BPJS'),
        sa.Column('task_name', sa.String(length=255), nullable=False, comment='Nama tugas'),
        sa.Column('task_type', sa.String(length=20), nullable=False, comment='Jenis tugas (registration, consultation, pharmacy, lab)'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='waiting', comment='Status tugas (waiting, active, completed)'),
        sa.Column('queue_number', sa.Integer(), nullable=True, comment='Nomor antrian'),
        sa.Column('estimated_time', sa.DateTime(timezone=True), nullable=True, comment='Perkiraan waktu pelayanan'),
        sa.Column('encounter_id', sa.Integer(), nullable=True, comment='Referensi ke encounter/kunjungan'),
        sa.Column('prescription_id', sa.Integer(), nullable=True, comment='Referensi ke resep (untuk task farmasi)'),
        sa.Column('lab_order_id', sa.Integer(), nullable=True, comment='Referensi ke pemeriksaan lab'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='Waktu mulai pengerjaan tugas'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='Waktu selesai pengerjaan tugas'),
        sa.Column('bpjs_response_data', postgresql.JSON(), nullable=True, comment='Response data lengkap dari BPJS'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Catatan tambahan untuk tugas'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp pembuatan record'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp update terakhir record'),
        sa.ForeignKeyConstraint(['booking_id'], ['bpjs_antrean_bookings.id'], name='fk_bpjs_antrean_tasks_booking_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['encounter_id'], ['encounters.id'], name='fk_bpjs_antrean_tasks_encounter_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['prescription_id'], ['prescriptions.id'], name='fk_bpjs_antrean_tasks_prescription_id', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lab_order_id'], ['lab_orders.id'], name='fk_bpjs_antrean_tasks_lab_order_id', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bpjs_antrean_tasks_id', 'bpjs_antrean_tasks', ['id'])
    op.create_index('ix_bpjs_antrean_tasks_booking_id', 'bpjs_antrean_tasks', ['booking_id'])
    op.create_index('ix_bpjs_antrean_tasks_task_id', 'bpjs_antrean_tasks', ['task_id'])
    op.create_index('ix_bpjs_antrean_tasks_task_type', 'bpjs_antrean_tasks', ['task_type'])
    op.create_index('ix_bpjs_antrean_tasks_status', 'bpjs_antrean_tasks', ['status'])
    op.create_index('ix_bpjs_antrean_tasks_encounter_id', 'bpjs_antrean_tasks', ['encounter_id'])
    op.create_index('ix_bpjs_antrean_tasks_prescription_id', 'bpjs_antrean_tasks', ['prescription_id'])
    op.create_index('ix_bpjs_antrean_tasks_lab_order_id', 'bpjs_antrean_tasks', ['lab_order_id'])

    # Create bpjs_antrean_status_updates table
    op.create_table(
        'bpjs_antrean_status_updates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False, comment='Referensi ke booking BPJS'),
        sa.Column('old_status', sa.String(length=20), nullable=False, comment='Status sebelumnya'),
        sa.Column('new_status', sa.String(length=20), nullable=False, comment='Status baru'),
        sa.Column('update_time', sa.DateTime(timezone=True), nullable=False, comment='Waktu perubahan status'),
        sa.Column('sync_status', sa.String(length=20), nullable=False, server_default='pending', comment='Status sinkronisasi dengan BPJS'),
        sa.Column('bpjs_response', postgresql.JSON(), nullable=True, comment='Respons lengkap dari API BPJS'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Pesan error jika sinkronisasi gagal'),
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='User yang melakukan update status'),
        sa.Column('update_source', sa.String(length=50), nullable=False, server_default='system', comment='Sumber update (system, mobile_jkn, manual)'),
        sa.Column('notes', sa.Text(), nullable=True, comment='Catatan tambahan untuk update status'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp pembuatan record'),
        sa.ForeignKeyConstraint(['booking_id'], ['bpjs_antrean_bookings.id'], name='fk_bpjs_antrean_status_updates_booking_id', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], name='fk_bpjs_antrean_status_updates_updated_by', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bpjs_antrean_status_updates_id', 'bpjs_antrean_status_updates', ['id'])
    op.create_index('ix_bpjs_antrean_status_updates_booking_id', 'bpjs_antrean_status_updates', ['booking_id'])
    op.create_index('ix_bpjs_antrean_status_updates_new_status', 'bpjs_antrean_status_updates', ['new_status'])
    op.create_index('ix_bpjs_antrean_status_updates_update_time', 'bpjs_antrean_status_updates', ['update_time'])
    op.create_index('ix_bpjs_antrean_status_updates_created_at', 'bpjs_antrean_status_updates', ['created_at'])


def downgrade():
    # Drop tables in reverse order of creation
    op.drop_index('ix_bpjs_antrean_status_updates_created_at', table_name='bpjs_antrean_status_updates')
    op.drop_index('ix_bpjs_antrean_status_updates_update_time', table_name='bpjs_antrean_status_updates')
    op.drop_index('ix_bpjs_antrean_status_updates_new_status', table_name='bpjs_antrean_status_updates')
    op.drop_index('ix_bpjs_antrean_status_updates_booking_id', table_name='bpjs_antrean_status_updates')
    op.drop_index('ix_bpjs_antrean_status_updates_id', table_name='bpjs_antrean_status_updates')
    op.drop_table('bpjs_antrean_status_updates')

    op.drop_index('ix_bpjs_antrean_tasks_lab_order_id', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_prescription_id', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_encounter_id', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_status', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_task_type', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_task_id', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_booking_id', table_name='bpjs_antrean_tasks')
    op.drop_index('ix_bpjs_antrean_tasks_id', table_name='bpjs_antrean_tasks')
    op.drop_table('bpjs_antrean_tasks')

    op.drop_index('ix_bpjs_antrean_bookings_sep_number', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_referral_number', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_bpjs_task_id', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_status', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_booking_date', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_doctor_id', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_poli_id', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_patient_id', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_appointment_id', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_booking_code', table_name='bpjs_antrean_bookings')
    op.drop_index('ix_bpjs_antrean_bookings_id', table_name='bpjs_antrean_bookings')
    op.drop_table('bpjs_antrean_bookings')

    op.drop_index('ix_bpjs_antrean_sync_logs_referenced_entity', table_name='bpjs_antrean_sync_logs')
    op.drop_index('ix_bpjs_antrean_sync_logs_created_at', table_name='bpjs_antrean_sync_logs')
    op.drop_index('ix_bpjs_antrean_sync_logs_status', table_name='bpjs_antrean_sync_logs')
    op.drop_index('ix_bpjs_antrean_sync_logs_endpoint', table_name='bpjs_antrean_sync_logs')
    op.drop_table('bpjs_antrean_sync_logs')

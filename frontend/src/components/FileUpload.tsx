'use client';

import { useState, useRef, DragEvent } from 'react';
import { uploadFile, getIndexingStatus } from '../lib/api';
import { Spinner, ErrorBanner } from './LoadingStates';
import styles from './FileUpload.module.css';

interface Props {
  onUploadSuccess?: () => void;
}

export default function FileUpload({ onUploadSuccess }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processUpload(e.target.files[0]);
    }
  };

  const processUpload = async (file: File) => {
    setError(null);
    setSuccessMsg(null);
    setIsUploading(true);
    
    try {
      const res = await uploadFile(file);
      
      let isDone = false;
      while (!isDone) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const statusRes = await getIndexingStatus();
        if (statusRes.status === 'ready') {
            isDone = true;
            setSuccessMsg(statusRes.message || res.message);
        } else if (statusRes.status === 'error') {
            isDone = true;
            throw new Error(statusRes.message);
        }
      }

      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className={styles.container}>
      {error && <div className={styles.alertWrap}><ErrorBanner message={error} onRetry={() => setError(null)} /></div>}
      
      <div 
        className={`${styles.dropzone} ${isDragging ? styles.dragging : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleChange} 
          className={styles.hiddenInput}
          accept=".csv,.pdf,.xlsx,.xls,.docx"
        />
        
        {isUploading ? (
          <div className={styles.uploadingState}>
            <Spinner size={24} />
            <p>Uploading and indexing...</p>
          </div>
        ) : (
          <div className={styles.idleState}>
            <div className={styles.icon}>⇧</div>
            <p className={styles.title}>Click or drag file to upload</p>
            <p className={styles.subtitle}>CSV, PDF, XLSX, DOCX (Max 20MB)</p>
          </div>
        )}
      </div>
      
      {successMsg && <p className={styles.successMsg}>{successMsg}</p>}
    </div>
  );
}

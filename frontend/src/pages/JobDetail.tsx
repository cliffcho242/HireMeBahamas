import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { Job } from '../types/job';

const JobDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (id) {
      fetchJob();
    }
  }, [id]);

  const fetchJob = async () => {
    try {
      const response = await api.get(`/jobs/${id}`);
      setJob(response.data);
    } catch (error) {
      console.error('Error fetching job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    setApplying(true);
    try {
      await api.post(`/jobs/${id}/apply`);
      alert('Application submitted successfully!');
    } catch (error) {
      console.error('Error applying for job:', error);
      alert('Error submitting application. Please try again.');
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading job details...</div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-600">Job not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
            <p className="text-xl text-gray-600 mb-2">{job.company}</p>
            <p className="text-gray-500">{job.location}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
              <div className="mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
                <div className="prose text-gray-700 whitespace-pre-wrap">
                  {job.description}
                </div>
              </div>

              {job.requirements && (
                <div className="mb-8">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements</h2>
                  <div className="prose text-gray-700 whitespace-pre-wrap">
                    {job.requirements}
                  </div>
                </div>
              )}

              {job.benefits && (
                <div className="mb-8">
                  <h2 className="text-xl font-semibulous text-gray-900 mb-4">Benefits</h2>
                  <div className="prose text-gray-700 whitespace-pre-wrap">
                    {job.benefits}
                  </div>
                </div>
              )}
            </div>

            <div>
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium text-gray-500">Category</span>
                    <p className="text-gray-900 capitalize">{job.category}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">Job Type</span>
                    <p className="text-gray-900 capitalize">{job.job_type}</p>
                  </div>
                  {job.salary_min && job.salary_max && (
                    <div>
                      <span className="text-sm font-medium text-gray-500">Salary Range</span>
                      <p className="text-gray-900">
                        ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                      </p>
                    </div>
                  )}
                  <div>
                    <span className="text-sm font-medium text-gray-500">Posted</span>
                    <p className="text-gray-900">
                      {new Date(job.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              {user && user.id !== job.employer_id && (
                <button
                  onClick={handleApply}
                  disabled={applying}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {applying ? 'Applying...' : 'Apply for this Job'}
                </button>
              )}

              {!user && (
                <div className="text-center">
                  <p className="text-gray-600 mb-4">Sign in to apply for this job</p>
                  <button
                    onClick={() => navigate('/login')}
                    className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Sign In
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetail;
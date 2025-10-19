import { Link } from 'react-router-dom';
import { MapPinIcon, ClockIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import { Job } from '../types/job';
import { formatDistanceToNow } from 'date-fns';

interface JobCardProps {
  job: Job;
}

const JobCard = ({ job }: JobCardProps) => {
  return (
    <Link to={`/jobs/${job.id}`} className="block">
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 h-full">
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800 line-clamp-2 flex-1 mr-2">
            {job.title}
          </h3>
          <span className="bg-bahamas-blue text-white text-xs px-2 py-1 rounded-full whitespace-nowrap">
            {job.category}
          </span>
        </div>

        <p className="text-gray-600 text-sm mb-4 line-clamp-3">
          {job.description}
        </p>

        <div className="flex items-center text-sm text-gray-500 mb-2">
          <CurrencyDollarIcon className="h-4 w-4 mr-1" />
          <span className="font-medium text-gray-700">
            {job.budget ? `$${job.budget.toLocaleString()}` : 'Salary not specified'}
            {job.budgetType === 'hourly' && '/hr'}
          </span>
        </div>

        <div className="flex items-center text-sm text-gray-500 mb-2">
          <MapPinIcon className="h-4 w-4 mr-1" />
          <span>{job.location}</span>
          {job.isRemote && (
            <span className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
              Remote
            </span>
          )}
        </div>

        <div className="flex items-center text-sm text-gray-500 mb-4">
          <ClockIcon className="h-4 w-4 mr-1" />
          <span>Posted {formatDistanceToNow(new Date(job.created_at))} ago</span>
        </div>

        {job.skills && job.skills.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {job.skills.slice(0, 3).map((skill, index) => (
              <span
                key={index}
                className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
              >
                {skill}
              </span>
            ))}
            {job.skills.length > 3 && (
              <span className="text-xs text-gray-500">
                +{job.skills.length - 3} more
              </span>
            )}
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {job.client?.profileImage ? (
              <img
                src={job.client.profileImage}
                alt={`${job.client.first_name} ${job.client.last_name}`}
                className="w-8 h-8 rounded-full mr-2"
              />
            ) : job.client ? (
              <div className="w-8 h-8 bg-gray-300 rounded-full mr-2 flex items-center justify-center">
                <span className="text-xs text-gray-600">
                  {job.client.first_name[0]}{job.client.last_name[0]}
                </span>
              </div>
            ) : null}
            {job.client && (
              <div>
                <p className="text-sm font-medium text-gray-800">
                  {job.client.first_name} {job.client.last_name}
                </p>
                {job.client.rating && (
                  <div className="flex items-center">
                    <span className="text-yellow-400 text-sm">★</span>
                    <span className="text-xs text-gray-600 ml-1">
                      {job.client.rating.toFixed(1)}
                    </span>
                  </div>
                )}
              </div>
            )}
          </div>
          
          <span className="text-sm font-medium text-bahamas-blue">
            {job.applications?.length || 0} proposals
          </span>
        </div>
      </div>
    </Link>
  );
};

export default JobCard;
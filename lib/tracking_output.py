import collections
import pickle
import os.path
from lib.objects_to_drive import ObjectsToDrive
from typing import Any, TypeVar

_T0 = TypeVar('_T0')

OUTPUT_FOLDER = "output"
TRACKINGS_FILENAME = "trackings.pickle"
TRACKINGS_FILE = OUTPUT_FOLDER + "/" + TRACKINGS_FILENAME


class TrackingOutput:

  def save_trackings(self, config, trackings) -> None:
    old_trackings = self.get_existing_trackings(config)
    merged_trackings = self.merge_trackings(old_trackings, trackings)
    self._write_merged(config, merged_trackings)

  def _write_merged(self, config, merged_trackings) -> None:
    groups_dict = collections.defaultdict(list)
    for tracking in merged_trackings:
      groups_dict[tracking.group].append(tracking)

    if not os.path.exists(OUTPUT_FOLDER):
      os.mkdir(OUTPUT_FOLDER)

    with open(TRACKINGS_FILE, 'wb') as output:
      pickle.dump(groups_dict, output)

    if 'driveFolder' in config:
      objects_to_drive = ObjectsToDrive()
      objects_to_drive.save(config['driveFolder'], TRACKINGS_FILENAME,
                            TRACKINGS_FILE)

  # Adds each Tracking object to the appropriate group
  # if there isn't already an entry for that tracking number
  def merge_trackings(self, old_trackings: _T0, trackings) -> _T0:
    old_tracking_numbers = set([ot.tracking_number for ot in old_trackings])
    for tracking in trackings:
      if tracking.tracking_number not in old_tracking_numbers:
        old_trackings.append(tracking)
    return old_trackings

  def get_existing_trackings(self, config) -> Any:
    if 'driveFolder' in config:
      objects_to_drive = ObjectsToDrive()
      from_drive = objects_to_drive.load(config['driveFolder'],
                                         TRACKINGS_FILENAME)
      if from_drive:
        return self._convert_to_list(from_drive)

    print(
        "Drive folder ID not present or we couldn't load from drive. Loading from local"
    )
    if not os.path.exists(TRACKINGS_FILE):
      return {}

    with open(TRACKINGS_FILE, 'rb') as tracking_file_stream:
      trackings_dict = pickle.load(tracking_file_stream)
    return self._convert_to_list(trackings_dict)

  def _convert_to_list(self, trackings_dict):
    result = []
    for trackings in trackings_dict.values():
      result.extend(trackings)
    return result

  def clear(self) -> None:
    # self.write_merged([])
    pass
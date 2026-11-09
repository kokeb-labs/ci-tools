// Seeded violation: a result kept in a struct member, then read after a second call of the same function.
#include <cstdlib>

namespace kv::rule_25_5_3_ordered_use::bad_stored {

struct Cache {
  const char* path;
};

bool path_starts_like_home() {
  const Cache cache{std::getenv("PATH")};
  const char* const home = std::getenv("HOME");
  return (cache.path != nullptr) && (home != nullptr) && (cache.path[0] == home[0]);  // seeded
}

}  // namespace kv::rule_25_5_3_ordered_use::bad_stored

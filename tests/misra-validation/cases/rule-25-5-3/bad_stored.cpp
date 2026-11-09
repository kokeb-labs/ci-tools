// Seeded violation: a getenv result kept in an object, then read after a second getenv call.
#include <cstdlib>

namespace kv::rule_25_5_3::bad_stored {

struct Settings {
  const char* home;
};

bool home_matches_user() {
  const Settings settings{std::getenv("HOME")};  // seeded: clang-tidy
  const char* const user = std::getenv("USER");  // seeded: clang-tidy
  return (settings.home != nullptr) && (user != nullptr) && (settings.home[0] == user[0]);  // seeded: codeql
}

}  // namespace kv::rule_25_5_3::bad_stored

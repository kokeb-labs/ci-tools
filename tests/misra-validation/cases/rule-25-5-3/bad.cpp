// Seeded violation: a returned static buffer read after a second call may have overwritten it.
#include <cstdlib>

namespace kv::rule_25_5_3::bad {

bool same_value() {
  const char* const first = std::getenv("FIRST");
  const char* const second = std::getenv("SECOND");
  return first == second;
}

struct Settings {
  const char* home;
};

void remember(Settings& settings) { settings.home = std::getenv("HOME"); }

}  // namespace kv::rule_25_5_3::bad

// Seeded violation: strerror's first result read after a second call, and its result kept in an object.
#include <cstdint>
#include <cstring>

namespace kv::rule_25_5_3_strerror::bad {

bool same_message(std::int32_t a, std::int32_t b) {
  const char* const first = std::strerror(a);
  const char* const second = std::strerror(b);
  return (first != nullptr) && (second != nullptr) && (first[0] == second[0]);
}

struct Report {
  const char* text;
};

void describe(Report& report, std::int32_t code) { report.text = std::strerror(code); }

}  // namespace kv::rule_25_5_3_strerror::bad

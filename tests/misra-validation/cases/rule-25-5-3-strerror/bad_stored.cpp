// Seeded violation: a result kept in a struct member, then read after a second call of the same function.
#include <cstdint>
#include <cstring>

namespace kv::rule_25_5_3_strerror::bad_stored {

struct Report {
  const char* text;
};

bool same_as_kept(std::int32_t kept, std::int32_t code) {
  const Report report{std::strerror(kept)};
  const char* const now = std::strerror(code);
  return (report.text != nullptr) && (now != nullptr) && (report.text[0] == now[0]);  // seeded
}

}  // namespace kv::rule_25_5_3_strerror::bad_stored

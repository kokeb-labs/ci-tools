// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_11::bad_edge {

struct Handle {
  Handle() = default;
  Handle(Handle const&) = default;
  Handle& operator=(Handle const&) = default;
  ~Handle() { value = 0; }
  std::int32_t value{0};
};

std::int32_t log_values(std::int32_t count, ...);

std::int32_t use() {
  Handle h;
  return log_values(1, h);  // seeded
}

}  // namespace kv::rule_8_2_11::bad_edge

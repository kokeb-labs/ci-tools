// Seeded violation: an object with a virtual member function goes through an ellipsis.
#include <cstdint>

namespace kv::rule_8_2_11_trivial::bad {

struct Probe {
  virtual ~Probe() = default;
  virtual std::int32_t read() const { return 0; }
};

std::int32_t first(std::int32_t count, ...);

std::int32_t use() {
  Probe p;
  return first(1, p);
}

}  // namespace kv::rule_8_2_11_trivial::bad

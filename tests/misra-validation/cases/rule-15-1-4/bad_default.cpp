// Seeded violation (default): a defaulted default constructor leaves a scalar member uninitialised.
#include <cstdint>

namespace kv::rule_15_1_4::bad_default {

class Gauge {
 public:
  Gauge() = default;  // seeded

  [[nodiscard]] std::uint32_t level() const { return level_; }

 private:
  std::uint32_t level_;
};

}  // namespace kv::rule_15_1_4::bad_default

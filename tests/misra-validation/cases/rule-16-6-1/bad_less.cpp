// Seeded violation: member operator- and operator<.
#include <cstdint>

namespace kv::rule_16_6_1::bad_less {

class Level {
 public:
  explicit Level(std::int32_t v) : v_(v) {}
  Level operator-(const Level& other) const { return Level(v_ - other.v_); }
  bool operator<(const Level& other) const { return v_ < other.v_; }

 private:
  std::int32_t v_;
};

}  // namespace kv::rule_16_6_1::bad_less

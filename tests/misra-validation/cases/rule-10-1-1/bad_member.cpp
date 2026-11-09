// Seeded violation (member): a member function taking a non-const reference it only reads.
#include <cstdint>

namespace kv::rule_10_1_1::bad_member {

struct Config {
  std::int32_t gain = 1;
};

class Amp {
 public:
  std::int32_t scaled(Config& c) const { return c.gain * level_; }  // seeded

 private:
  std::int32_t level_ = 2;
};

}  // namespace kv::rule_10_1_1::bad_member

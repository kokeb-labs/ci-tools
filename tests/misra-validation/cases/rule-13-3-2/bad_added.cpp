// Seeded violation (added): an overrider gives a default argument to a parameter that has none in the base.
#include <cstdint>

namespace kv::rule_13_3_2::bad_added {

class Filter {
 public:
  virtual ~Filter() = default;
  virtual std::int32_t apply(std::int32_t gain) const { return gain; }
};

class Offset : public Filter {
 public:
  std::int32_t apply(std::int32_t gain = 5) const override { return gain; }  // seeded
};

std::int32_t run(const Offset& f) { return f.apply(); }

}  // namespace kv::rule_13_3_2::bad_added
